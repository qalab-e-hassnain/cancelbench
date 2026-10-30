# Upstream tool-contract probes

These are narrow interface probes, not results for complete agents. No model, production endpoint, PostgreSQL instance, or human speech was used. No upstream defect is established.

## Reproduction

Download the public repositories and check out the exact commits recorded in probes.json. Run:

```sh
python3 scripts/probe_upstream_contracts.py --speculative-root /path/to/speculative-action --riley-root /path/to/riley-agent
```

The script rejects unexpected commits or modified inspected files. It AST-extracts the original function body and executes it with controlled dependencies rather than importing the full application. The Speculative Actions dictionary mutation is original code; Riley's dispatch uses a fake API, so its observed mutation is not a PostgreSQL result. File hashes are recorded.

## Controlled schedule

Each worker pauses before tool entry. The harness retracts authorization by advancing its own version, then releases the worker. Neither function accepts this version, so both proceed. A local wrapper checking that version suppresses both calls. This expected interface result does not show that upstream orchestrators ignore cancellation. The wrapper is not an authoritative boundary: corrections after its check remain unprotected, as the separate SQLite demo illustrates.

## Code ledger

| Implementation | Inspected paths and findings | Remaining unknowns |
| --- | --- | --- |
| [Speculative Actions](https://github.com/naimengye/speculative-action/tree/dc938b9ef7474caf07fe4ad16549c1fa8c7d268c) | `e-commerce/tau-bench/tau_bench/envs/retail/tools/cancel_pending_order.py`, `CancelPendingOrder.invoke` mutates a dictionary without an intent epoch. `envs/base.py`, `Env.step` invokes tools. The tool description requests explicit confirmation. | Whether callers invalidate queued work before entry; remote effects; other domains. |
| [Riley OpenAI Realtime mini](https://github.com/veris-ai/riley-agent/tree/f54b220e21cd55d812e7a4386ea865d4791b6b98) | `openai-realtime-mini/app/tools.py`, `dispatch` forwards arguments; `app/main.py` invokes dispatch on completed function arguments; `app/db.py`, `Database.update_card_status` updates by card ID without an intent epoch predicate. | Provider cancellation semantics, complete correction handling, other variants and deployment configuration. |

Business cancellation of an order/card differs from retracting a pending agent operation. The probes concern the latter; business method names do not imply task-control guarantees.

## Novelty implication

The interface question is where a retraction becomes binding on a queued/dispatched effect. No new algorithm or failure class has been established. Next steps require full-runtime adapters, documented cancellation promises, acknowledgment semantics, and actual commit/dispatch measurements. Compare corrections before entry, after entry/before commit, after commit/before notification, and after notification.
