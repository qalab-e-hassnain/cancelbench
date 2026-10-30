"""Reproduce a correction between an application check and a SQLite write."""

import json
import sqlite3


def run_case(atomic):
    database = sqlite3.connect(":memory:")
    try:
        database.executescript(
            "CREATE TABLE intent (version INTEGER NOT NULL);"
            "INSERT INTO intent VALUES (1);"
            "CREATE TABLE assignment (version INTEGER, target TEXT);"
        )
        operation_version = 1
        application_check = database.execute("SELECT version FROM intent").fetchone()[0]
        database.execute("UPDATE intent SET version = 2")
        database.commit()
        if atomic:
            database.execute(
                "INSERT INTO assignment SELECT ?, ? WHERE "
                "(SELECT version FROM intent) = ?",
                (operation_version, "305", operation_version),
            )
        elif application_check == operation_version:
            database.execute("INSERT INTO assignment VALUES (?, ?)", (operation_version, "305"))
        database.commit()
        assignment = database.execute("SELECT version, target FROM assignment").fetchone()
        return {"atomic_boundary": atomic, "latest_intent": 2, "assignment": assignment,
                "obsolete_write_accepted": assignment is not None}
    finally:
        database.close()


def main():
    unsafe = run_case(False)
    guarded = run_case(True)
    if not unsafe["obsolete_write_accepted"] or guarded["obsolete_write_accepted"]:
        raise RuntimeError("Commit boundary demonstration violated its expected outcome")
    print(json.dumps({"scope": "Controlled SQLite interleaving; no audio, remote service, or distributed guarantee.",
                      "cases": [unsafe, guarded]}, indent=2))


if __name__ == "__main__":
    main()
