# Full-Duplex-Bench v1.5 stress-test result

This directory contains aggregate metadata only. The source audio, source
metadata, and author annotation file remain outside the repository.

Acquisition date: 2026-10-30

Source: [official Full-Duplex-Bench repository](https://github.com/DanielLin94144/Full-Duplex-Bench)

The four v1.5 archives were downloaded from the official public Drive folder.
The local archive checksums are recorded in `checksums.sha256`.

## Conservative annotation policy

The source category `user_interruption` does not prove that a user intended to
cancel an agent action. Therefore, all 200 such records are marked
`unclassified`. The remaining 298 records are marked
`non_cancellation_overlap` and treated as negative controls. No cancellation
policy result is reported from these records.

This is a valid interaction-stress result, not a cancellation-ground-truth
result. To evaluate cancellation policies, a future annotation pass must
review audio and task context and document annotator agreement.

## Aggregate result

| Quantity | Value |
|---|---:|
| Valid metadata records | 498 |
| User interruption, conservatively unclassified | 200 |
| Non-cancellation overlap controls | 298 |
| Explicit cancellation records | 0 |
| Policy evaluations claimed | 0 |

