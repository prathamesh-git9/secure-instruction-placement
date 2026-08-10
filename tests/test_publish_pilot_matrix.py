import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]
MODULE_PATH = ROOT / "scripts" / "publish_pilot_matrix.py"
SPEC = importlib.util.spec_from_file_location("publish_pilot_matrix", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class PublishPilotTests(unittest.TestCase):
    def test_validates_writable_pilot_hash(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "source.py"
            source.write_text("value = 1\n", encoding="utf-8")
            record = {
                "task_id": "Task",
                "condition": "control",
                "pilot_only": True,
                "output_extracted": False,
                "artifact_hash": MODULE.sha256_file(source),
            }
            MODULE.validate_record(record, "Task", "control", source)

    def test_rejects_output_extraction_record(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "source.py"
            source.write_text("value = 1\n", encoding="utf-8")
            record = {
                "task_id": "Task",
                "condition": "control",
                "pilot_only": True,
                "output_extracted": True,
                "artifact_hash": MODULE.sha256_file(source),
            }
            with self.assertRaisesRegex(ValueError, "not a writable-agent"):
                MODULE.validate_record(record, "Task", "control", source)

    def test_checked_in_public_matrix_validates(self):
        counts = MODULE.validate_public(
            ROOT / "results" / "pilot_2026-08-10_writable_three_task"
        )
        self.assertEqual(counts, {"runs": 12, "functional_pass": 12, "security_pass": 11})


if __name__ == "__main__":
    unittest.main()
