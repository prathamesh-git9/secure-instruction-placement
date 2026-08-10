import copy
import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]
MODULE_PATH = ROOT / "scripts" / "validate_task_subset.py"
SPEC = importlib.util.spec_from_file_location("validate_task_subset", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class TaskSubsetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = json.loads(
            (ROOT / "configs" / "task_subset.json").read_text(encoding="utf-8")
        )

    def test_checked_in_subset_is_valid(self):
        counts = MODULE.validate(self.config)
        self.assertEqual(counts["total"], 13)
        self.assertEqual(counts["included"], 11)
        self.assertEqual(counts["excluded"], 2)
        self.assertGreaterEqual(counts["weakness_families"], 5)

    def test_rejects_undetected_included_seed(self):
        value = copy.deepcopy(self.config)
        included = next(task for task in value["tasks"] if task["status"] == "include")
        included["seed_detected"] = False
        with self.assertRaisesRegex(ValueError, "no detected vulnerable seed"):
            MODULE.validate(value)

    def test_rejects_exclusion_without_reason(self):
        value = copy.deepcopy(self.config)
        excluded = next(task for task in value["tasks"] if task["status"] == "exclude")
        excluded.pop("exclusion_reason")
        with self.assertRaisesRegex(ValueError, "no reason"):
            MODULE.validate(value)


if __name__ == "__main__":
    unittest.main()

