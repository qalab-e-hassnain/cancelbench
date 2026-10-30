# Public-data validation inputs

This directory contains metadata and manifests only. Source audio and
transcripts must be downloaded from the official dataset hosts into a local
directory outside this repository.

## Register a local dataset

```sh
python3 scripts/validate_dataset_manifest.py \
  --manifest datasets/manifest.json
```

The manifest deliberately records access URLs, licenses, intended use, and
the expected evaluation boundary. It does not contain audio, transcripts,
SAS URLs, API keys, or private QuickComm identifiers.

For a local Full-Duplex-Bench checkout, create a metadata-only index with:

```sh
python3 scripts/ingest_full_duplex.py \
  --root /path/to/Full-Duplex-Bench/v1_5 \
  --output /tmp/cancelbench-full-duplex.jsonl
```

The output contains relative audio paths and overlap timestamps only. It does
not copy audio or include transcript text.

To evaluate only explicitly annotated cancellation events:

```sh
PYTHONPATH=src python3 scripts/evaluate_full_duplex.py \
  --metadata /tmp/cancelbench-full-duplex.jsonl \
  --annotations datasets/full_duplex_annotations.example.json \
  --output /tmp/cancelbench-full-duplex-results.jsonl
```

The example annotation file is illustrative. It must not be reported as a
dataset result; real annotations require audio review and an exclusion log.

When a dataset is downloaded, record its version, split, download date, local
path, and SHA-256 checksum in a separate local run manifest. Do not commit
source files or derived personal data.

