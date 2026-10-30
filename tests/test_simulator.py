import unittest

from cancelbench.simulator import POLICIES, Policy, Scenario, scenarios, simulate


class SimulatorTests(unittest.TestCase):
    def run_case(self, policy="eager", **kwargs):
        p = next(p for p in POLICIES if p.name == policy)
        return simulate(Scenario("unit", **kwargs), p)

    def test_analytic_stable_latency(self):
        for prep in (100, 500, 1200):
            for p in POLICIES:
                row, _ = simulate(Scenario("unit", kind="stable", prepare_initial_ms=prep), p)
                expected = prep if p.mode == "wait" else max(0, prep - 1000)
                if p.mode == "guarded":
                    expected = max(prep, 1000 + p.grace_ms) - 1000
                self.assertEqual(row["settlement_latency_ms"], expected)
                self.assertTrue(row["final_correct"])

    def test_cancel_before_commit_prevents_effect(self):
        row, trace = self.run_case(kind="cancel", change_ms=150, prepare_initial_ms=1200)
        self.assertTrue(row["cancel_prevented"])
        self.assertTrue(row["final_correct"])
        self.assertFalse(any(e["event"] == "committed" for e in trace))

    def test_cancel_after_commit_is_not_prevention(self):
        row, _ = self.run_case(kind="cancel", change_ms=450, prepare_initial_ms=100)
        self.assertFalse(row["cancel_prevented"])
        self.assertTrue(row["cancel_final_correct"])
        self.assertEqual(row["compensations"], 1)

    def test_equal_time_cancellation_precedes_commit(self):
        row, _ = self.run_case(kind="cancel", change_ms=500, prepare_initial_ms=500)
        self.assertTrue(row["cancel_prevented"])

    def test_delayed_delivery_limits_world_freshness(self):
        row, _ = self.run_case(change_ms=450, prepare_initial_ms=500, delivery_ms=100)
        self.assertFalse(row["stale_known_commit"])
        self.assertTrue(row["stale_world_commit"])

    def test_no_fence_allows_old_write_to_win(self):
        row, _ = self.run_case("guarded_no_fence", change_ms=150,
                               prepare_initial_ms=1200, prepare_revised_ms=100)
        self.assertFalse(row["final_correct"])
        self.assertTrue(row["stale_known_commit"])

    def test_fence_blocks_same_late_write(self):
        row, _ = self.run_case("guarded_0", change_ms=150,
                               prepare_initial_ms=1200, prepare_revised_ms=100)
        self.assertTrue(row["final_correct"])
        self.assertFalse(row["stale_known_commit"])

    def test_delayed_compensation_does_not_clear_new_write(self):
        row, trace = self.run_case(change_ms=450, prepare_initial_ms=100,
                                   prepare_revised_ms=100, compensation_ms=250)
        self.assertTrue(row["final_correct"])
        self.assertTrue(any(e["event"] == "compensation_noop" for e in trace))
        self.assertEqual(trace[-1]["db_target"], "503")

    def test_notification_history_survives_compensation(self):
        row, trace = self.run_case(kind="cancel", change_ms=450,
                                   prepare_initial_ms=100, notification_ms=0)
        self.assertTrue(row["final_correct"])
        self.assertTrue(row["superseded_notification"])
        self.assertEqual(sum(e["event"] == "notified" for e in trace), 1)

    def test_revision_can_suppress_pending_notification(self):
        row, _ = self.run_case(kind="cancel", change_ms=150,
                               prepare_initial_ms=100, notification_ms=200)
        self.assertEqual(row["blocked_notifications"], 1)
        self.assertFalse(row["superseded_notification"])

    def test_noop_interruption_keeps_task(self):
        for p in POLICIES:
            a, _ = simulate(Scenario("a", kind="stable"), p)
            b, _ = simulate(Scenario("b", kind="noop"), p)
            for key in ("final_correct", "settlement_latency_ms", "preparations", "compensations"):
                self.assertEqual(a[key], b[key])

    def test_entire_grid_invariants(self):
        for s in scenarios():
            for p in POLICIES:
                row, trace = simulate(s, p)
                self.assertEqual([e["time_ms"] for e in trace], sorted(e["time_ms"] for e in trace))
                if p.fence:
                    self.assertFalse(row["stale_known_commit"], (s, p))
                    self.assertTrue(row["final_correct"], (s, p))

    def test_invalid_configuration(self):
        with self.assertRaises(ValueError):
            Scenario("bad", delivery_ms=-1)
        with self.assertRaises(ValueError):
            Policy("bad", "unknown")


if __name__ == "__main__":
    unittest.main()
