import copy
import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]
MODULE_PATH = ROOT / "scripts" / "validate_study_design.py"
SPEC = importlib.util.spec_from_file_location("validate_study_design", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class StudyDesignTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.subset = json.loads((ROOT / "configs" / "task_subset.json").read_text())
        cls.split = json.loads((ROOT / "configs" / "study_split.json").read_text())
        cls.design = json.loads(
            (ROOT / "configs" / "confirmatory_design.json").read_text()
        )

    def test_checked_in_design_is_valid_draft(self):
        result = MODULE.validate(self.subset, self.split, self.design)
        self.assertEqual(result["development_tasks"], 3)
        self.assertEqual(result["holdout_tasks"], 8)
        self.assertEqual(result["excluded_tasks"], 2)
        self.assertEqual(result["holdout_families"], 5)
        self.assertEqual(result["planned_runs_per_agent"], 96)

    def test_rejects_overlap_between_development_and_holdout(self):
        split = copy.deepcopy(self.split)
        split["confirmatory_holdout_tasks"].append(
            split["development_tasks"][0]["task_id"]
        )
        with self.assertRaisesRegex(ValueError, "overlapping"):
            MODULE.validate(self.subset, split, self.design)

    def test_frozen_design_requires_review_agent_and_budget(self):
        design = copy.deepcopy(self.design)
        design["status"] = "frozen"
        with self.assertRaisesRegex(ValueError, "review"):
            MODULE.validate(self.subset, self.split, design)


if __name__ == "__main__":
    unittest.main()

