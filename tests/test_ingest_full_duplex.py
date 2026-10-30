import json
import tempfile
import unittest
from pathlib import Path

from scripts.ingest_full_duplex import iter_records


class FullDuplexIngestTests(unittest.TestCase):
    def test_metadata_is_normalized_without_audio_content(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            sample = root / "v1_5" / "user_interruption" / "sample-001"
            sample.mkdir(parents=True)
            (sample / "input.wav").write_bytes(b"placeholder")
            (sample / "metadata.json").write_text(json.dumps({
                "context_text": "context",
                "current_turn_text": "please cancel that",
                "timestamps": [1.25, 2.5],
            }))
            records = list(iter_records(root))
            self.assertEqual(len(records), 1)
            self.assertEqual(records[0]["overlap_start_ms"], 1250)
            self.assertEqual(records[0]["overlap_end_ms"], 2500)
            self.assertEqual(records[0]["audio_path"], "v1_5/user_interruption/sample-001/input.wav")
            self.assertNotIn("context_text", records[0])
            self.assertNotIn("current_turn_text", records[0])


if __name__ == "__main__":
    unittest.main()
