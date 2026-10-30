# Open-data validation plan

## Purpose

The QuickComm production records are useful for a private case study, but the
current storage state does not support a reproducible public audio release:
the database contains relative audio paths and the referenced latest objects
were not found in either configured Azure container. Therefore, the public
paper should validate the cancellation protocol on openly accessible data and
report QuickComm only as an aggregate deployment context unless separate
consent and retention approval permits de-identified release.

## Recommended validation set

| Priority | Dataset/benchmark | What it validates | Use in this paper | Boundary |
|---|---|---|---|---|
| 1 | [SpokenWOZ](https://spokenwoz.github.io/) | Spoken task-oriented dialogue, natural disfluency, ASR noise, dialogue state and acts | Replay spoken turns as user input; map requests to cancellable and non-cancellable tasks; measure cancellation correctness and task preservation | CC BY-NC 4.0; it is human-human dialogue, not an agent-cancellation dataset |
| 2 | [Full-Duplex-Bench](https://full-duplex-bench.github.io/) | User interruption, pause handling, backchanneling, turn-taking | Stress-test cancellation during speech overlap and interruption timing; report false cancellation and late cancellation separately | Its stimuli/metrics target turn-taking, so cancellation semantics must be added by this project |
| 3 | [AMI Meeting Corpus](https://groups.inf.ed.ac.uk/ami/corpus/) | Natural multi-speaker overlap, timestamps, dialogue acts | Robustness check for background speech, overlap, and accidental cancellation triggers | Meeting speech is not hotel/security task traffic; use only as an interaction-stress set |
| 4 | [HumDial-FDBench](https://github.com/ASLP-lab/HumDial-FDBench) | Human-recorded interruption and rejection scenarios | Optional focused test set for cancellation/rejection behavior | Verify the repository's current license and access terms before redistribution |

## Experimental protocol

1. Keep the existing deterministic oracle simulator as the primary causal
   benchmark. It isolates cancellation timing from ASR and model variation.
2. Build a public replay adapter that consumes only dataset transcripts,
   timestamps, and permitted audio; do not upload any source audio or private
   QuickComm content to this repository.
3. Define a fixed event taxonomy before evaluation:
   `cancel_before_entry`, `cancel_after_check`,
   `cancel_after_commit_before_notify`, `cancel_after_notify`,
   `non_cancellation_overlap`, and `false_cancellation`.
4. Evaluate at least these metrics:
   - cancellation precision and recall;
   - task-state safety violations;
   - notifications suppressed after cancellation;
   - cancellation-to-notification latency;
   - false cancellations during backchannels/background speech;
   - replay coverage and exclusion counts.
5. Report results separately by dataset and by event class. Do not pool them
   into one score because the datasets measure different phenomena.
6. Use the same policy grid already in the repository (`immediate`,
   `guarded_0`, `guarded_500`, `guarded_1000`, and debounce) and add a fixed
   random seed only where audio segmentation introduces randomness.
7. Release manifests, hashes, preprocessing code, metric code, and aggregate
   outputs. Release no private recordings, raw transcripts containing personal
   data, SAS URLs, credentials, or derived clips unless the source license and
   consent explicitly allow it.

## Minimum publishable validation

The minimum credible public experiment is SpokenWOZ plus
Full-Duplex-Bench, with the existing simulator retained as the controlled
causal experiment. AMI and HumDial-FDBench are useful robustness extensions,
not prerequisites for the first submission.

## QuickComm evidence plan

For QuickComm, preserve only aggregate facts in the paper until the audio
objects are recovered and research-use consent is documented:

- 421 hotel conversations and 164 security conversations;
- 576 records with audio links and 585 with non-empty stored transcripts;
- approximately 75.4 minutes of linked audio by recorded duration;
- 93 hotel/security tasks, 85 linked to conversations;
- all 585 conversation intent labels currently appear as `fallback`, which
  should be treated as a data-quality limitation rather than a semantic result.

These values were obtained through read-only queries on 2026-10-30. They are
deployment-context statistics, not a released benchmark and not evidence that
the cancellation policy generalizes without the open-data validation above.

## Dataset access and license checks

Before downloading or redistributing any dataset, record its version,
download date, license, split, and checksum in an experiment manifest. Do not
mirror source audio in this repository. A public result should link to the
official source and provide the exact preprocessing commands instead.

