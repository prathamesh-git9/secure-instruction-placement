import importlib.util
import math
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).parents[1] / "scripts" / "summarize_results.py"
SPEC = importlib.util.spec_from_file_location("summarize_results", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class SummaryTests(unittest.TestCase):
    def test_parse_bool(self):
        self.assertTrue(MODULE.parse_bool("yes"))
        self.assertFalse(MODULE.parse_bool("0"))
        with self.assertRaises(ValueError):
            MODULE.parse_bool("maybe")

    def test_wilson_interval_bounds(self):
        low, high = MODULE.wilson_interval(5, 10)
        self.assertGreaterEqual(low, 0)
        self.assertLessEqual(high, 1)
        self.assertLess(low, 0.5)
        self.assertGreater(high, 0.5)

    def test_primary_and_conditional_security_rates(self):
        rows = [
            {"condition": "control", "agent": "a", "task_id": "1", "functional_pass": True, "security_pass": True},
            {"condition": "control", "agent": "a", "task_id": "2", "functional_pass": True, "security_pass": False},
            {"condition": "control", "agent": "a", "task_id": "3", "functional_pass": False, "security_pass": True},
        ]
        record = MODULE.summarise(rows, ["condition", "agent"])[0]
        self.assertEqual(record["secure_and_correct"], 1)
        self.assertAlmostEqual(record["secure_and_correct_rate"], 1 / 3)
        self.assertEqual(record["vulnerable_among_functionally_correct"], 1)
        self.assertAlmostEqual(record["vulnerability_rate_among_correct"], 0.5)
        self.assertFalse(math.isnan(record["secure_and_correct_ci_low"]))


if __name__ == "__main__":
    unittest.main()
