"""Run the complete fixed grid and write auditable, deterministic artifacts."""

import argparse
import csv
import gzip
import hashlib
import io
import json
from pathlib import Path
import platform
from statistics import mean, median

from .monotonicity import analyse, effects
from .simulator import POLICIES, scenarios, simulate


def summarize(rows):
    changed = [r for r in rows if r["kind"] in {"revise", "cancel", "chain"}]
    cancel = [r for r in rows if r["kind"] == "cancel"]
    stable = [r for r in rows if r["kind"] == "stable"]
    success_latency = [r["settlement_latency_ms"] for r in rows if r["final_correct"]]
    rate = lambda data, key: mean(int(r[key]) for r in data) if data else None
    return {
        "runs": len(rows), "changed_runs": len(changed), "cancel_runs": len(cancel),
        "final_correct_rate": rate(rows, "final_correct"),
        "stale_known_commit_rate": rate(rows, "stale_known_commit"),
        "stale_world_commit_rate": rate(rows, "stale_world_commit"),
        "changed_superseded_commit_rate": rate(changed, "superseded_commit"),
        "changed_superseded_notification_rate": rate(changed, "superseded_notification"),
        "stale_world_notification_rate": rate(rows, "stale_world_notification"),
        "cancel_prevented_rate": rate(cancel, "cancel_prevented"),
        "cancel_final_correct_rate": rate(cancel, "cancel_final_correct"),
        "cancel_notice_prevented_rate": rate(cancel, "cancel_notice_prevented"),
        "mean_success_settlement_ms": mean(success_latency) if success_latency else None,
        "median_success_settlement_ms": median(success_latency) if success_latency else None,
        "stable_mean_settlement_ms": mean(r["settlement_latency_ms"] for r in stable) if stable else None,
        "mean_preparations": mean(r["preparations"] for r in rows),
        "total_compensations": sum(r["compensations"] for r in rows),
    }


def report(summary):
    header = "| Policy | Runs | Final correct | Known-stale commit | World-stale commit | Superseded notification* | Stable latency (ms) |\n"
    header += "| --- | ---: | ---: | ---: | ---: | ---: | ---: |\n"
    for name, a in summary.items():
        header += (f"| {name} | {a['runs']} | {a['final_correct_rate']:.2%} | "
                   f"{a['stale_known_commit_rate']:.2%} | {a['stale_world_commit_rate']:.2%} | "
                   f"{a['changed_superseded_notification_rate']:.2%} | {a['stable_mean_settlement_ms']:.1f} |\n")
    return header + "\n*Among revision/cancellation/chain scenarios; retrospective, not necessarily unauthorized at emission.\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("results"))
    args = parser.parse_args()
    out = args.output
    out.mkdir(parents=True, exist_ok=True)
    cases = list(scenarios())
    case_bytes = ("\n".join(json.dumps(s.__dict__, sort_keys=True) for s in cases) + "\n").encode()
    (out / "scenarios.jsonl").write_bytes(case_bytes)
    rows, eff = [], {}
    # Explicit mtime and blank original filename make gzip bytes reproducible.
    with (out / "traces.jsonl.gz").open("wb") as raw:
        with gzip.GzipFile(filename="", fileobj=raw, mode="wb", mtime=0) as compressed:
            with io.TextIOWrapper(compressed, encoding="utf-8", newline="\n") as trace_file:
                for s in cases:
                    for policy in POLICIES:
                        row, trace = simulate(s, policy)
                        rows.append(row)
                        eff[s.id, policy.name] = effects(trace)
                        trace_file.write(json.dumps({"scenario_id": s.id, "policy": policy.name,
                                                     "events": trace}, sort_keys=True) + "\n")
    with (out / "runs.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    summary = {p.name: summarize([r for r in rows if r["policy"] == p.name]) for p in POLICIES}
    (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    (out / "summary.md").write_text(report(summary))
    stratified = {}
    for p in POLICIES:
        for kind in ("stable", "noop", "revise", "cancel", "chain"):
            stratified[f"{p.name}/{kind}"] = summarize([r for r in rows if r["policy"] == p.name and r["kind"] == kind])
    (out / "by_kind.json").write_text(json.dumps(stratified, indent=2) + "\n")
    # Explicit sensitivity tables preserve denominators for transport and timing.
    sensitivity = []
    for p in POLICIES:
        for delay in (0, 100, 350):
            for t in (150, 450, 850, 1050, 1350, 1800):
                subset = [r for r in rows if r["policy"] == p.name and r["delivery_ms"] == delay
                          and r["change_ms"] == t and r["kind"] in {"revise", "cancel", "chain"}]
                sensitivity.append({"policy": p.name, "delivery_ms": delay, "change_ms": t, **summarize(subset)})
    (out / "sensitivity.json").write_text(json.dumps(sensitivity, indent=2) + "\n")
    by_key = {(r["id"], r["policy"]): r for r in rows}
    (out / "monotonicity.json").write_text(json.dumps(analyse(cases, POLICIES, eff, by_key), indent=2) + "\n")
    manifest = {
        "experiment": "cancelbench-fixed-grid-v1", "time_unit": "virtual milliseconds",
        "python": platform.python_version(), "scenario_count": len(cases), "run_count": len(rows),
        "scenario_sha256": hashlib.sha256(case_bytes).hexdigest(),
        "source_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in sorted(Path(__file__).parent.glob("*.py"))},
        "artifacts_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                             for p in sorted(out.iterdir()) if p.name != "manifest.json" and p.is_file()},
        "scope": "Oracle intent events; no audio, LLM, network, real SQL or human participants.",
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"Completed {len(cases)} scenarios × {len(POLICIES)} policies = {len(rows)} runs.")
    print(report(summary))


if __name__ == "__main__":
    main()
