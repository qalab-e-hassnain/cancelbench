import unittest

from cancelbench.monotonicity import analyse, effects
from cancelbench.simulator import POLICIES, Scenario, scenarios, simulate


class MonotonicityTests(unittest.TestCase):
    def test_release_gate_holds_only_the_notification(self):
        p = next(p for p in POLICIES if p.name == "release_gate")
        row, trace = simulate(Scenario("unit", kind="cancel", change_ms=450, prepare_initial_ms=100), p)
        self.assertFalse(row["cancel_prevented"])
        self.assertTrue(row["cancel_notice_prevented"])
        self.assertTrue(row["final_correct"])
        self.assertTrue(any(e["event"] == "notification_blocked" for e in trace))

    def test_full_grid_release_monotonicity(self):
        cases = list(scenarios())
        eff, rows = {}, {}
        for s in cases:
            for p in POLICIES:
                row, trace = simulate(s, p)
                eff[s.id, p.name], rows[s.id, p.name] = effects(trace), row
        result = analyse(cases, POLICIES, eff, rows)
        for pair in result["ordered_pairs"] + result["endpoint_sweep"]:
            self.assertEqual(pair["notice_violation"], 0, pair)
            self.assertEqual(pair["commit_violation"], 0, pair)
            self.assertEqual(pair["more_superseded"], 0, pair)
        for pair in result["ordered_pairs"]:
            self.assertEqual(pair["prevention_worse"], 0, pair)
        self.assertEqual(result["release_gate_equals_guarded_0_notices"], len(cases))
        self.assertEqual(result["closed_form"]["matched"], result["closed_form"]["checked"])
        # The two unordered policies each win somewhere: neither dominates per scenario.
        unordered = result["unordered_pairs"][0]
        self.assertGreater(unordered["fewer_superseded"], 0)
        self.assertGreater(unordered["more_superseded"], 0)


if __name__ == "__main__":
    unittest.main()
