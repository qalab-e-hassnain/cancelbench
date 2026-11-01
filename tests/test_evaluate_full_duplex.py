import json
import tempfile
import unittest
from pathlib import Path

from cancelbench.simulator import POLICIES
from scripts.evaluate_full_duplex import evaluate


class FullDuplexEvaluationTests(unittest.TestCase):
    def test_overlap_is_negative_control_unless_explicitly_annotated(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            metadata = root / "metadata.jsonl"
            annotations = root / "annotations.json"
            output = root / "results.jsonl"
            metadata.write_text(json.dumps({"id": "sample-1"}) + "\n")
            annotations.write_text(json.dumps({
                "sample-1": {"event_class": "non_cancellation_overlap"}
            }))
            rows = evaluate(metadata, annotations)
            self.assertEqual(rows, [{
                "id": "sample-1",
                "status": "negative_control",
                "event_class": "non_cancellation_overlap",
            }])

    def test_explicit_cancel_runs_all_policies(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            metadata = root / "metadata.jsonl"
            annotations = root / "annotations.json"
            metadata.write_text(json.dumps({"id": "sample-2"}) + "\n")
            annotations.write_text(json.dumps({
                "sample-2": {
                    "event_class": "cancel_before_entry",
                    "change_ms": 450,
                    "turn_end_ms": 1000,
                    "prepare_initial_ms": 500,
                }
            }))
            rows = evaluate(metadata, annotations)
            self.assertEqual(len(rows), len(POLICIES))
            self.assertTrue(all(row["status"] == "evaluated" for row in rows))


if __name__ == "__main__":
    unittest.main()
