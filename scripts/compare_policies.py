"""Compare additional receipt-debounce baselines without replacing paper results."""

import argparse
import hashlib
import json
from pathlib import Path

from cancelbench.run import summarize
from cancelbench.simulator import POLICIES, Policy, scenarios, simulate


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("experiments/debounce/comparison.json"))
    args = parser.parse_args()
    policies = POLICIES + tuple(
        Policy(f"debounce_{window}", "debounce", grace_ms=window)
        for window in (200, 500, 1000)
    )
    cases = list(scenarios())
    summaries = {}
    for policy in policies:
        rows = [simulate(scenario, policy)[0] for scenario in cases]
        summaries[policy.name] = {
            "overall": summarize(rows),
            "by_kind": {
                kind: summarize([row for row in rows if row["kind"] == kind])
                for kind in ("stable", "noop", "revise", "cancel", "chain")
            },
        }
    artifact = {
        "scope": "Deterministic oracle simulation; virtual latency; no speech results.",
        "debounce_semantics": "Commit after preparation and receipt plus window; fenced obsolete work is rejected. Noop interruptions do not reset the window.",
        "scenario_count": len(cases),
        "scenario_sha256": hashlib.sha256(json.dumps([scenario.__dict__ for scenario in cases], sort_keys=True).encode()).hexdigest(),
        "simulator_sha256": hashlib.sha256((Path(__file__).resolve().parents[1] / "src/cancelbench/simulator.py").read_bytes()).hexdigest(),
        "policies": summaries,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(artifact, indent=2) + "\n")
    print(f"Wrote {len(cases)} scenarios x {len(policies)} policies to {args.output}")


if __name__ == "__main__":
    main()
