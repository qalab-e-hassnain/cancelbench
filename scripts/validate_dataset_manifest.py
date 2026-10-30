"""Validate the public-data manifest without downloading any source data."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib.parse import urlparse


REQUIRED_DATASETS = {"spokenwoz", "full_duplex_bench", "ami", "humdial_fdbench"}
REQUIRED_FIELDS = {
    "id",
    "name",
    "official_url",
    "license",
    "role",
    "required_for_minimum_public_validation",
    "evaluation_boundary",
    "local_path",
    "version",
    "split",
}


def validate(path: Path) -> list[str]:
    data = json.loads(path.read_text())
    errors: list[str] = []
    if data.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    policy = data.get("policy", {})
    if policy.get("source_audio_in_repo") is not False:
        errors.append("source_audio_in_repo must be false")
    if policy.get("private_quickcomm_data_in_repo") is not False:
        errors.append("private_quickcomm_data_in_repo must be false")

    datasets = data.get("datasets")
    if not isinstance(datasets, list):
        return ["datasets must be a list"]
    seen: set[str] = set()
    for index, item in enumerate(datasets):
        prefix = f"datasets[{index}]"
        missing = REQUIRED_FIELDS - set(item)
        errors.extend(f"{prefix} missing {field}" for field in sorted(missing))
        dataset_id = item.get("id")
        if dataset_id in seen:
            errors.append(f"{prefix} duplicate id {dataset_id}")
        seen.add(dataset_id)
        parsed = urlparse(item.get("official_url", ""))
        if parsed.scheme != "https" or not parsed.netloc:
            errors.append(f"{prefix} official_url must be an HTTPS URL")
    missing_ids = REQUIRED_DATASETS - seen
    errors.extend(f"missing dataset {dataset_id}" for dataset_id in sorted(missing_ids))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=Path("datasets/manifest.json"))
    args = parser.parse_args()
    errors = validate(args.manifest)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"OK: {args.manifest} contains {len(REQUIRED_DATASETS)} registered public datasets")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
