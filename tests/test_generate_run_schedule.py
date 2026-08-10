import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]
MODULE_PATH = ROOT / "scripts" / "generate_run_schedule.py"
SPEC = importlib.util.spec_from_file_location("generate_run_schedule", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class RunScheduleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.design = json.loads(
            (ROOT / "configs" / "confirmatory_design.json").read_text()
        )

    def test_schedule_is_deterministic_and_balanced(self):
        first = MODULE.build_rows(self.design)
        second = MODULE.build_rows(self.design)
        self.assertEqual(first, second)
        string_rows = [{key: str(value) for key, value in row.items()} for row in first]
        counts = MODULE.validate_rows(string_rows, self.design)
        self.assertEqual(counts, {"runs": 96, "blocks": 3, "tasks": 8, "conditions": 4})

    def test_rejects_incomplete_block(self):
        rows = MODULE.build_rows(self.design)
        rows.pop()
        string_rows = [{key: str(value) for key, value in row.items()} for row in rows]
        with self.assertRaisesRegex(ValueError, "expected 96"):
            MODULE.validate_rows(string_rows, self.design)

    def test_write_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "schedule.csv"
            MODULE.write_schedule(self.design, output)
            with self.assertRaisesRegex(ValueError, "refusing to overwrite"):
                MODULE.write_schedule(self.design, output)


if __name__ == "__main__":
    unittest.main()

