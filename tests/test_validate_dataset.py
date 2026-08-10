import importlib.util
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).parents[1] / "scripts" / "validate_dataset.py"
SPEC = importlib.util.spec_from_file_location("validate_dataset", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class ValidateManifestTests(unittest.TestCase):
    def valid_manifest(self):
        return {
            "task_id": "task_01",
            "title": "Example valid task",
            "language": "Python",
            "cwe": ["CWE-79"],
            "source": {
                "name": "Source",
                "url": "https://example.com/source",
                "revision": "abc123",
                "retrieved_at": "2026-08-10",
            },
            "license": {
                "spdx": "Apache-2.0",
                "evidence_url": "https://example.com/license",
                "adaptation_allowed": True,
            },
            "commands": {
                "functional_test": ["python -m unittest functional"],
                "security_test": ["python -m unittest security"],
            },
        }

    def test_valid_manifest(self):
        self.assertEqual(MODULE.validate_manifest(self.valid_manifest(), Path("manifest.json")), [])

    def test_rejects_missing_adaptation_permission(self):
        data = self.valid_manifest()
        data["license"]["adaptation_allowed"] = False
        errors = MODULE.validate_manifest(data, Path("manifest.json"))
        self.assertTrue(any("adaptation permission" in error for error in errors))

    def test_requires_separate_security_test(self):
        data = self.valid_manifest()
        data["commands"]["security_test"] = []
        errors = MODULE.validate_manifest(data, Path("manifest.json"))
        self.assertTrue(any("commands.security_test" in error for error in errors))


if __name__ == "__main__":
    unittest.main()

