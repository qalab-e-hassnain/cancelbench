# Local asynchronous cancellation-contract experiment

Run `python3 scripts/runtime_races.py`. Eight deterministic cases execute two local boundary implementations under four controlled asyncio schedules. Tests live in tests/test_runtime_races.py. This is a reference testbed, not an evaluation of upstream full agents.

## Contract and observations

The contract is declared before execution: after receipt of cancellation, old-version writes and notification acceptance must be rejected at their authoritative boundaries. Earlier writes are compensated; notification history persists. Both intent and effects live in one SQLite database. Each guarded check-and-insert is one SQL statement without an intervening await. This does not model atomicity across a remote service.

| Correction timing | Application check only | Authoritative checks |
| --- | --- | --- |
| Before tool entry | Prevents write and notification | Prevents write and notification |
| After application check, before write | Old write and notification accepted; final state wrong | Write rejected; final state empty |
| After write, before notification | Database recovered, but stale notification accepted | Database recovered; notification rejected |
| After notification | Database recovered; earlier notification remains | Database recovered; earlier notification remains |

The final row is retrospective supersession, not received-stale execution. A successful cancellation acknowledgment must distinguish prevention, compensation, and already-emitted effects. Recorded acknowledgments are computed at quiescence, not implemented as live spoken responses.

These cases establish executable examples of metric disagreement, not prevalence or novelty. The local guard's success follows from the declared atomic SQL boundary. SQLite notification rows model acceptance/history, not actual email, delivery, human observation, or an external queue.

## Full-system execution status

The inspected Riley application needs a provider session and PostgreSQL; its documented simulation path additionally uses Veris tooling/account access. No provider-backed run was performed. Speculative Actions' complete model-driven trajectories were not run either. Earlier extracted-function probes remain narrower than complete applications. Do not report these eight cases as failures or successes of either upstream system.

Next full-system adapters must preserve actual provider/tool semantics and record correction receipt and cancellation acknowledgment separately. Real notification delivery requires a stated dispatch contract, persistent log/outbox semantics, and fault tests; the shared SQLite boundary cannot establish those guarantees.
