import unittest
from pathlib import Path

from scripts.validate_dataset_manifest import validate


class DatasetManifestTests(unittest.TestCase):
    def test_public_manifest_is_safe_and_complete(self):
        errors = validate(Path("datasets/manifest.json"))
        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
