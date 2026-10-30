import unittest

from cancelbench.simulator import Policy, Scenario, simulate


class DebounceTests(unittest.TestCase):
    def run_case(self, grace_ms=300, **kwargs):
        return simulate(Scenario("debounce", **kwargs),
                        Policy("debounce", "debounce", grace_ms))

    def test_stable_waits_for_preparation_and_grace(self):
        for prep, grace, expected in ((100, 300, 300), (500, 300, 500),
                                      (100, 0, 100)):
            with self.subTest(prep=prep, grace=grace):
                row, trace = self.run_case(grace, kind="stable", prepare_initial_ms=prep)
                self.assertTrue(row["final_correct"])
                self.assertEqual([e["time_ms"] for e in trace
                                  if e["event"] == "committed"], [expected])

    def test_revision_uses_receipt_time_and_fences_old_work(self):
        row, trace = self.run_case(change_ms=100, delivery_ms=50,
                                   prepare_initial_ms=100, prepare_revised_ms=50)
        self.assertTrue(row["final_correct"])
        self.assertEqual(row["blocked_commits"], 1)
        self.assertEqual([(e["version"], e["time_ms"]) for e in trace
                          if e["event"] == "committed"], [(2, 450)])

    def test_cancellation_during_grace_prevents_commit(self):
        row, trace = self.run_case(kind="cancel", change_ms=200,
                                   prepare_initial_ms=100)
        self.assertTrue(row["cancel_prevented"])
        self.assertTrue(row["final_correct"])
        self.assertEqual(row["blocked_commits"], 1)
        self.assertFalse(any(e["event"] == "committed" for e in trace))

    def test_noop_does_not_reset_grace(self):
        row, trace = self.run_case(kind="noop", change_ms=200, prepare_initial_ms=100)
        self.assertTrue(row["final_correct"])
        self.assertEqual(row["preparations"], 1)
        self.assertEqual([e["time_ms"] for e in trace
                          if e["event"] == "committed"], [300])

    def test_equal_time_receipt_fences_commit(self):
        for kind in ("revise", "cancel"):
            with self.subTest(kind=kind):
                row, trace = self.run_case(kind=kind, change_ms=250, delivery_ms=50,
                                           prepare_initial_ms=100, prepare_revised_ms=50)
                self.assertTrue(row["final_correct"])
                self.assertEqual(row["blocked_commits"], 1)
                self.assertFalse(any(e["event"] == "committed" and e["version"] == 1
                                     for e in trace))
                if kind == "revise":
                    self.assertEqual([e["time_ms"] for e in trace
                                      if e["event"] == "committed"], [600])
                else:
                    self.assertTrue(row["cancel_prevented"])


if __name__ == "__main__":
    unittest.main()
