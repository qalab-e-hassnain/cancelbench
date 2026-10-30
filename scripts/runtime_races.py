"""Deterministic async runtime races against a local SQLite effect boundary."""

import argparse
import asyncio
import json
from pathlib import Path
import sqlite3


STAGES = ("before_entry", "after_check", "after_commit", "after_notification")


async def run_case(stage, authoritative=True):
    database = sqlite3.connect(":memory:")
    database.executescript(
        "CREATE TABLE intent(version INTEGER); INSERT INTO intent VALUES(1);"
        "CREATE TABLE assignment(version INTEGER, target TEXT);"
        "CREATE TABLE notifications(version INTEGER, target TEXT);"
    )
    reached, release = asyncio.Event(), asyncio.Event()
    trace = []

    def record(event):
        trace.append({"sequence": len(trace), "event": event})

    async def barrier(location):
        if stage == location:
            record("paused_" + location)
            reached.set()
            await release.wait()

    async def worker():
        await barrier("before_entry")
        accepted = database.execute("SELECT version FROM intent").fetchone()[0] == 1
        record("application_check_accepted" if accepted else "application_check_rejected")
        if not accepted:
            return
        await barrier("after_check")
        if authoritative:
            database.execute(
                "INSERT INTO assignment SELECT 1, '305' WHERE (SELECT version FROM intent)=1"
            )
        else:
            database.execute("INSERT INTO assignment VALUES(1, '305')")
        committed = database.execute("SELECT COUNT(*) FROM assignment").fetchone()[0] > 0
        database.commit()
        record("committed" if committed else "commit_rejected")
        await barrier("after_commit")
        if committed:
            if authoritative:
                database.execute(
                    "INSERT INTO notifications SELECT 1, '305' WHERE (SELECT version FROM intent)=1"
                )
            else:
                database.execute("INSERT INTO notifications VALUES(1, '305')")
            database.commit()
            record("notified" if database.execute("SELECT COUNT(*) FROM notifications").fetchone()[0]
                   else "notification_rejected")
        await barrier("after_notification")

    async def correction():
        await reached.wait()
        database.execute("UPDATE intent SET version=2")
        database.execute("DELETE FROM assignment WHERE version=1")
        database.commit()
        record("cancellation_received_and_compensated")
        release.set()

    try:
        await asyncio.wait_for(asyncio.gather(worker(), correction()), timeout=5)
        final_empty = database.execute("SELECT COUNT(*) FROM assignment").fetchone()[0] == 0
        notification_count = database.execute("SELECT COUNT(*) FROM notifications").fetchone()[0]
        correction_index = next(item["sequence"] for item in trace
                                if item["event"] == "cancellation_received_and_compensated")
        stale_commit = any(item["event"] == "committed" and item["sequence"] > correction_index
                           for item in trace)
        stale_notification = any(item["event"] == "notified" and item["sequence"] > correction_index
                                 for item in trace)
        committed_any = any(item["event"] == "committed" for item in trace)
        acknowledgment = ("notification_already_emitted" if notification_count else
                          "database_effect_compensated" if final_empty and committed_any else
                          "prevented" if final_empty else "cancellation_contract_violated")
        return {"stage": stage, "authoritative": authoritative,
                "final_empty": final_empty, "prevented": not committed_any,
                "received_stale_commit": stale_commit,
                "received_stale_notification": stale_notification,
                "notification_history_count": notification_count,
                "acknowledgment_at_quiescence": acknowledgment, "trace": trace}
    finally:
        database.close()


async def experiment():
    return [await run_case(stage, authoritative)
            for authoritative in (False, True) for stage in STAGES]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("experiments/runtime/races.json"))
    args = parser.parse_args()
    artifact = {"scope": "Local asyncio runtime, deterministic barriers, SQLite database and notification ledger; no external delivery or speech.",
                "contract": "After cancellation receipt, no older-version commit or notification may be accepted at its authoritative boundary. Earlier committed assignment is compensated; emitted notifications persist.",
                "cases": asyncio.run(experiment())}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(artifact, indent=2) + "\n")
    print(f"Wrote {len(artifact['cases'])} runtime race cases to {args.output}")


if __name__ == "__main__":
    main()
