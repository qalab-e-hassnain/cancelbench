# Additional baseline experiment

Run `PYTHONPATH=src python3 scripts/compare_policies.py` from the repository root. The JSON records scenario and simulator hashes and overall/per-kind summaries. This extension is separate from the original manuscript tables.

All numbers are deterministic finite-grid properties, not voice-system measurements. Receipt debounce waits until both preparation is ready and the substantive receipt plus its window have elapsed. Fencing rejects obsolete operations. Non-cancelling interruptions do not reset the window. This is not a speech silence detector.

The initial execution contains 1,764 paired scenarios across nine configurations (15,876 runs). Guarded(0) has 43.78% retrospectively superseded notifications on changed scenarios; debounce(1000) has 42.59%. Both have 50% cancellation prevention and 66.7 ms stable residual settlement latency on this grid. Therefore these comparisons do not establish superiority of the fixed gate. Stable latency is clipped relative to the nominal turn boundary and is not actual response time; per-kind latency and the full timing distributions need further study.

The example supports testing a safety/latency trade-off rather than assuming the proposed gate is better. No significance test is appropriate for interpreting this exhaustive synthetic grid as a human population sample. The new summaries have not received the original trace-audit pipeline's independent rescoring; existing simulator unit tests and original six-policy reproduction have passed.
