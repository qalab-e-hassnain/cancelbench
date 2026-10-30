"""Independently rescore saved traces and verify artifact hashes."""

import argparse
import csv
import gzip
import hashlib
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path, default=Path("results"))
    args = parser.parse_args()
    root = args.results
    manifest = json.loads((root / "manifest.json").read_text())
    for name, expected in manifest["artifacts_sha256"].items():
        actual = hashlib.sha256((root / name).read_bytes()).hexdigest()
        if actual != expected:
            raise ValueError(f"Artifact hash mismatch: {name}")
    for name, expected in manifest["source_sha256"].items():
        actual = hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
        if actual != expected:
            raise ValueError(f"Source hash mismatch: {name}")
    with (root / "runs.csv").open(newline="") as f:
        rows = {(r["id"], r["policy"]): r for r in csv.DictReader(f)}
    checked = 0
    seen = set()
    with gzip.open(root / "traces.jsonl.gz", "rt") as f:
        for line in f:
            item = json.loads(line)
            key = (item["scenario_id"], item["policy"])
            if key in seen:
                raise ValueError(f"Duplicate trace: {key}")
            seen.add(key)
            r = rows[key]
            events = item["events"]
            source = [e for e in events if e["event"] in {"source_set", "source_cancel"}]
            final = source[-1]
            commits = [e for e in events if e["event"] == "committed"]
            notices = [e for e in events if e["event"] == "notified"]
            correct = events[-1]["db_target"] == final["target"]
            changed = r["kind"] in {"revise", "cancel", "chain"}
            expected = {
                "final_correct": correct,
                "stale_known_commit": any(e["version"] != e["received_version"] for e in commits),
                "stale_world_commit": any(e["version"] != e["world_version"] for e in commits),
                "stale_world_notification": any(e["version"] != e["world_version"] for e in notices),
                "superseded_commit": changed and any(e["version"] != final["version"] for e in commits),
                "superseded_notification": changed and any(e["version"] != final["version"] for e in notices),
                "cancel_prevented": r["kind"] == "cancel" and not commits,
                "cancel_final_correct": r["kind"] == "cancel" and correct,
            }
            for name, value in expected.items():
                if r[name] != str(bool(value)):
                    raise ValueError(f"Metric mismatch: {key} {name}")
            expected_latency = ""
            if correct:
                wrong_indices = [i for i, e in enumerate(events) if e["db_target"] != final["target"]]
                settled = events[wrong_indices[-1] + 1]["time_ms"] if wrong_indices else 0
                expected_latency = str(max(0, settled - max(int(r["turn_end_ms"]), final["time_ms"])))
            if r["settlement_latency_ms"] != expected_latency:
                raise ValueError(f"Latency mismatch: {key}")
            checked += 1
    if len(seen) != len(rows):
        raise ValueError("Trace / row cardinality mismatch")
    print(f"Verified artifact/source hashes and independently rescored {checked} traces.")


if __name__ == "__main__":
    main()
