"""Evaluate explicitly annotated Full-Duplex-Bench records.

Overlap is not treated as cancellation unless an annotation says so. Source
audio and transcript text remain outside the repository; this script consumes
only the metadata JSONL and a small author-created annotation JSON file.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from cancelbench.simulator import POLICIES, Scenario, simulate


CANCELLATION_CLASSES = {
    "cancel_before_entry",
    "cancel_after_check",
    "cancel_after_commit_before_notify",
    "cancel_after_notify",
}
VALID_CLASSES = CANCELLATION_CLASSES | {
    "non_cancellation_overlap",
    "false_cancellation",
    "unclassified",
}


def evaluate(metadata_path: Path, annotations_path: Path) -> list[dict]:
    annotations = json.loads(annotations_path.read_text())
    output: list[dict] = []
    for line in metadata_path.read_text().splitlines():
        record = json.loads(line)
        sample_id = record["id"]
        annotation = annotations.get(sample_id)
        if not annotation:
            output.append({"id": sample_id, "status": "excluded", "reason": "missing_annotation"})
            continue
        event_class = annotation.get("event_class")
        if event_class not in VALID_CLASSES:
            output.append({"id": sample_id, "status": "excluded", "reason": "invalid_event_class"})
            continue
        if event_class not in CANCELLATION_CLASSES:
            output.append({"id": sample_id, "status": "negative_control", "event_class": event_class})
            continue
        required = ("change_ms", "turn_end_ms", "prepare_initial_ms")
        if any(key not in annotation for key in required):
            output.append({"id": sample_id, "status": "excluded", "reason": "missing_timing_annotation"})
            continue
        scenario = Scenario(
            id=sample_id,
            kind="cancel",
            change_ms=int(annotation["change_ms"]),
            turn_end_ms=int(annotation["turn_end_ms"]),
            prepare_initial_ms=int(annotation["prepare_initial_ms"]),
            notification_ms=int(annotation.get("notification_ms", 200)),
            compensation_ms=int(annotation.get("compensation_ms", 250)),
        )
        for policy in POLICIES:
            result, _trace = simulate(scenario, policy)
            output.append({
                "id": sample_id,
                "status": "evaluated",
                "event_class": event_class,
                "policy": policy.name,
                "cancel_prevented": result["cancel_prevented"],
                "cancel_final_correct": result["cancel_final_correct"],
                "superseded_notification": result["superseded_notification"],
                "settlement_latency_ms": result["settlement_latency_ms"],
            })
    return output


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", type=Path, required=True)
    parser.add_argument("--annotations", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    rows = evaluate(args.metadata, args.annotations)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(json.dumps(row, sort_keys=True) for row in rows) + "\n")
    print(f"wrote {len(rows)} metadata-only evaluation rows to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
