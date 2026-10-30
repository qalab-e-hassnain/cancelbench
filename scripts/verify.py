"""Verify tests, reproduction, archived traces and manuscript consistency."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
ENV = {**os.environ, "PYTHONPATH": str(ROOT / "src")}


def run(*args):
    subprocess.run([sys.executable, *args], cwd=ROOT, env=ENV, check=True)


def main():
    run("-m", "unittest", "discover", "-s", "tests", "-v")
    run("-m", "cancelbench.audit", "--results", str(ROOT / "results"))
    with tempfile.TemporaryDirectory(prefix="cancelbench-reproduce-") as scratch:
        scratch = Path(scratch)
        outputs = scratch / "results"
        run("-m", "cancelbench.run", "--output", str(outputs))
        run("-m", "cancelbench.audit", "--results", str(outputs))
        manifest = json.loads((ROOT / "results/manifest.json").read_text())
        for name in manifest["artifacts_sha256"]:
            if (ROOT / "results" / name).read_bytes() != (outputs / name).read_bytes():
                raise ValueError(f"Reproduction differs: {name}")
        # Interpreter metadata may differ across machines; results must not.
        paper = scratch / "paper"
        run(str(ROOT / "scripts/build_paper.py"), "--results", str(outputs), "--output", str(paper))
        for name in ("manuscript.md", "manuscript.html", "manuscript.tex"):
            if (ROOT / "paper" / name).read_bytes() != (paper / name).read_bytes():
                raise ValueError(f"Manuscript is out of date: {name}")
    print("PASS: tests, archived trace audit, byte-identical result reproduction and manuscript consistency.")


if __name__ == "__main__":
    main()
