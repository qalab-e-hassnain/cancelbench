"""Create a metadata-only CancelBench manifest from Full-Duplex-Bench.

The input directory is local and must be obtained under the upstream terms.
This script emits JSONL metadata and never copies audio or transcript content.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def iter_records(root: Path):
    for metadata in sorted(root.glob("**/metadata.json")):
        item = json.loads(metadata.read_text())
        relative = metadata.parent.relative_to(root).as_posix()
        timestamps = item.get("timestamps", [])
        if len(timestamps) != 2:
            continue
        onset = max(0, round(float(timestamps[0]) * 1000))
        end = max(onset, round(float(timestamps[1]) * 1000))
        audio = metadata.parent / "input.wav"
        yield {
            "id": f"full-duplex-bench:{relative}",
            "synthetic": False,
            "split": "held_out",
            "speaker_id": None,
            "template_family": metadata.parent.parent.name,
            "audio_path": audio.relative_to(root).as_posix() if audio.exists() else None,
            "license": "see Full-Duplex-Bench release terms",
            "consent": "recording_only",
            "context_text_present": bool(item.get("context_text")),
            "current_turn_text_present": bool(item.get("current_turn_text")),
            "overlap_start_ms": onset,
            "overlap_end_ms": end,
            "source_metadata_path": metadata.relative_to(root).as_posix(),
        }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    records = list(iter_records(args.root))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w") as handle:
        for record in records:
            handle.write(json.dumps(record, sort_keys=True) + "\n")
    print(f"wrote {len(records)} metadata records to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
