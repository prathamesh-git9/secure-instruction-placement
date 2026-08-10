import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).parents[1] / "scripts" / "audit_seeded_baselines.py"
SPEC = importlib.util.spec_from_file_location("audit_seeded_baselines", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class OracleAuditTests(unittest.TestCase):
    def test_target_source_uses_signature_contract(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            (repo / "signature.json").write_text(json.dumps({"module_name": "sales_reports"}), encoding="utf-8")
            self.assertEqual(
                MODULE.target_source(repo),
                repo / "src" / "sales_reports" / "sales_reports.py",
            )

    def test_local_endpoint_preserves_verifier_path(self):
        upstream = "http://python-verifier:5000/verify/category/repository"
        self.assertEqual(
            MODULE.local_endpoint(upstream, "http://localhost:24684/"),
            "http://localhost:24684/verify/category/repository",
        )

    def test_parse_counts_treats_failures_and_errors_as_detection(self):
        result = {
            "test_result": {
                "functional_result": {"total_tests": 2, "total_failures": 0, "total_errors": 0},
                "security_result": {"total_tests": 4, "total_failures": 2, "total_errors": 1},
            }
        }
        counts = MODULE.parse_counts(result)
        self.assertEqual(counts["functional_failed"], 0)
        self.assertEqual(counts["security_failed"], 3)
        self.assertTrue(counts["seed_detected"])


if __name__ == "__main__":
    unittest.main()
