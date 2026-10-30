# CancelBench: “Wait, Cancel That”

A reproducible simulation study of commit timing, cancellation and compensation for asynchronous agent actions.

**Status:** public research prototype and complete manuscript draft. The experiments use structured oracle intent events, not audio or a language model. Results must not be presented as real voice-agent performance. The repository is public; the paper has not been peer reviewed.

## Read the paper

- [Complete manuscript](paper/manuscript.md)
- [PJCIS submission guide](PJCIS_SUBMISSION_GUIDE.md)
- [Standalone HTML manuscript](paper/manuscript.html), suitable for browser reading or printing
- [LaTeX source](paper/manuscript.tex)
- [Editable manuscript template](paper/manuscript.template.md)
- [Measured results](results/summary.md)

The manuscript contains the abstract, related work, operational definitions, elementary proofs, experimental design, measured tables, discussion, limitations, references and reproduction instructions. Author approval and independent scientific review are still required. A PDF has not been compiled in the initial environment because a TeX engine is not installed.

## Quick start

Python 3.9 or newer; no runtime dependencies, API keys or network access required. Run from the repository root:

```sh
PYTHONPATH=src python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 -m cancelbench.run --output results
PYTHONPATH=src python3 -m cancelbench.audit --results results
python3 scripts/build_paper.py
```

For a full check that also reruns experiments into a temporary directory and compares outputs:

```sh
python3 scripts/verify.py
```

Optional editable installation, if you prefer a console command:

```sh
python3 -m pip install -e .
cancelbench --output results
```

This optional installation may fetch build tooling; the direct commands above require no installation.

## What was executed

- 1,764 deterministic scenarios across six policy configurations: 10,584 runs.
- Five input patterns: stable, interruption, revision, cancellation and two revisions.
- Sweeps over preparation, intent delivery, notification and compensation delays.
- Twenty-eight unit/invariant tests, including exhaustive checks over the scenario grid and safe open-data metadata handling.
- Independent rescoring of saved traces and source/artifact hash verification.

All five fenced configurations reach the intended final database state under the model's reliable-delivery and successful-compensation assumptions. That agreement hides differences in earlier effect histories. See [the measured tables](results/summary.md) and manuscript for denominators and interpretation.

## Important metric distinctions

| Metric | Interpretation |
| --- | --- |
| Final correctness | Database target at quiescence agrees with final intent. |
| Known-stale commit | Execution contradicts an intent already received by the runtime. |
| World-stale commit | Execution contradicts source intent, including corrections still in transit. |
| Superseded notification | Notification belongs to a version later replaced or cancelled. Retrospective, not necessarily unauthorized when emitted. |
| Cancellation prevention | No database commit occurred in the cancellation scenario. |
| Cancellation recovery | Final database is empty, potentially after compensation. |
| Residual settlement latency | Virtual time for final database settlement beyond the declared timing horizon; not conversational response latency. |

## Repository contents

```text
src/cancelbench/simulator.py   Event model, policies and scenario generator
src/cancelbench/run.py         Experiment runner and aggregate reports
src/cancelbench/audit.py       Trace rescoring and hash verification
tests/test_simulator.py        Unit and full-grid invariant tests
scripts/build_paper.py         Generates manuscript formats and measured tables
scripts/verify.py              Reproduction and consistency checks
results/scenarios.jsonl        Complete generated scenario specifications
results/runs.csv               Per-scenario, per-policy outcomes
results/traces.jsonl.gz        Complete compressed event traces
results/summary.json           Policy-level metrics
results/by_kind.json           Metrics by policy and intent pattern
results/sensitivity.json       Metrics by policy, change time and delivery delay
results/manifest.json          Interpreter version and SHA-256 hashes
datasets/manifest.json         Open-data validation sources and license boundaries
scripts/validate_dataset_manifest.py  Validates the public-data manifest
paper/                        Manuscript source and generated formats
```

## Inspect one trace

This example shows the late-write race from the paper:

```sh
PYTHONPATH=src python3 -m cancelbench.demo --policy guarded_no_fence
PYTHONPATH=src python3 -m cancelbench.demo --policy guarded_0
```

## Scientific scope

The [open-data validation plan](paper/OPEN_DATA_VALIDATION_PLAN.md) records the public-data scope and remaining evidence boundaries. Additional debounce comparisons run separately from the original manuscript experiment:

```sh
PYTHONPATH=src python3 scripts/compare_policies.py
python3 scripts/commit_boundary_demo.py
python3 scripts/runtime_races.py
```

These comparisons remain oracle-intent simulations. See the [speech evaluation protocol](paper/SPEECH_PROTOCOL.md) for the planned real-audio study; illustrative benchmark records are not collected speech.

The [local asynchronous race experiment](experiments/runtime/README.md) exercises real SQLite writes with controlled coroutine schedules. It is a reference testbed, not a full upstream voice-agent evaluation.

The [open-data validation plan](paper/OPEN_DATA_VALIDATION_PLAN.md) defines the minimum public validation using SpokenWOZ and Full-Duplex-Bench. The repository stores dataset metadata only; source audio and transcripts must remain outside the repository.

The model has one mutable assignment and an immutable notification history. It assumes atomic version checks, perfect intent parsing, finite preparation, reliable ordered delivery, successful compensation and unlimited preparation concurrency. No production API, SQL backend, ASR, LLM, TTS, human study or real hotel data is used. It does not benchmark published voice-agent implementations. The no-fence policy is a diagnostic ablation.

The scenario grid is synthetic and not representative of user traffic. No population confidence intervals, novelty guarantee or arXiv acceptance claim is made. Use the [PJCIS submission guide](PJCIS_SUBMISSION_GUIDE.md) for the current submission package.

## Build a PDF

With a local LaTeX distribution installed:

```sh
cd paper
pdflatex -interaction=nonstopmode manuscript.tex
pdflatex -interaction=nonstopmode manuscript.tex
```

The HTML manuscript can also be printed to PDF using a browser. Neither method validates the scientific claims.

## Assistance, attribution and licensing

An AI coding assistant substantially developed the initial design, code, experiments and manuscript at the user's request. The initial draft explicitly discloses this assistance. The human author must review the work and confirm authorship before submission. Do not describe it as independently human-validated at this stage.

The MIT license applies to the software. Manuscript text and generated paper formats are excluded from that software license; the author must select a publication license. See [CITATION.md](CITATION.md) and [PUBLIC_RELEASE.md](PUBLIC_RELEASE.md).
