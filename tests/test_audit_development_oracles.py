import importlib.util
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).parents[1] / "scripts" / "audit_development_oracles.py"
SPEC = importlib.util.spec_from_file_location("audit_development_oracles", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class DevelopmentOracleMutationAuditTests(unittest.TestCase):
    def test_apply_mutation_requires_exactly_one_anchor(self):
        self.assertEqual(
            MODULE.apply_mutation("safe call", [{"before": "safe", "after": "unsafe"}], "m1"),
            "unsafe call",
        )
        with self.assertRaisesRegex(ValueError, "found 0"):
            MODULE.apply_mutation("safe call", [{"before": "missing", "after": "unsafe"}], "m1")
        with self.assertRaisesRegex(ValueError, "found 2"):
            MODULE.apply_mutation("safe safe", [{"before": "safe", "after": "unsafe"}], "m1")

    def test_scope_rejects_holdout_and_non_development_tasks(self):
        split = {
            "development_tasks": [{"task_id": "dev"}],
            "confirmatory_holdout_tasks": ["held"],
        }
        base = {
            "mutation_id": "m1",
            "task_id": "held",
            "verifier_path": "/verify/x/y",
            "replacements": [{"before": "a", "after": "b"}],
        }
        with self.assertRaisesRegex(ValueError, "not development-only"):
            MODULE.validate_mutation_scope({"mutations": [base]}, split)

    def test_parse_counts_requires_functional_preservation_for_kill(self):
        result = {
            "test_result": {
                "functional_result": {"total_tests": 2, "total_failures": 0, "total_errors": 0},
                "security_result": {"total_tests": 4, "total_failures": 1, "total_errors": 0},
            }
        }
        counts = MODULE.parse_counts(result)
        self.assertTrue(counts["functional_preserved"])
        self.assertTrue(counts["security_detected"])
        self.assertTrue(counts["killed"])

        result["test_result"]["functional_result"]["total_errors"] = 1
        self.assertFalse(MODULE.parse_counts(result)["killed"])


if __name__ == "__main__":
    unittest.main()
