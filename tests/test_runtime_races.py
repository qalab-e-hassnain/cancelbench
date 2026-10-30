import asyncio
from pathlib import Path
import sys
import unittest


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from runtime_races import run_case


class RuntimeRaceTests(unittest.TestCase):
    def test_application_check_leaves_late_write_race(self):
        row = asyncio.run(run_case("after_check", False))
        self.assertTrue(row["received_stale_commit"])
        self.assertFalse(row["final_empty"])

    def test_authoritative_boundary_rejects_late_write(self):
        row = asyncio.run(run_case("after_check", True))
        self.assertFalse(row["received_stale_commit"])
        self.assertTrue(row["prevented"])
        self.assertTrue(row["final_empty"])

    def test_compensation_does_not_make_prevention_true(self):
        row = asyncio.run(run_case("after_commit", True))
        self.assertTrue(row["final_empty"])
        self.assertFalse(row["prevented"])
        self.assertEqual(row["notification_history_count"], 0)

    def test_notification_needs_its_own_boundary_check(self):
        row = asyncio.run(run_case("after_commit", False))
        self.assertTrue(row["final_empty"])
        self.assertTrue(row["received_stale_notification"])

    def test_emitted_history_survives_compensation(self):
        row = asyncio.run(run_case("after_notification", True))
        self.assertTrue(row["final_empty"])
        self.assertEqual(row["notification_history_count"], 1)
        self.assertFalse(row["received_stale_notification"])
        self.assertEqual(row["acknowledgment_at_quiescence"], "notification_already_emitted")

    def test_cancel_before_entry_prevents_both_policies(self):
        for authoritative in (False, True):
            row = asyncio.run(run_case("before_entry", authoritative))
            self.assertTrue(row["prevented"])
            self.assertEqual(row["notification_history_count"], 0)
