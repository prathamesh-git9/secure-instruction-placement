import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).parents[1] / "scripts" / "materialize_condition.py"
SPEC = importlib.util.spec_from_file_location("materialize_condition", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class MaterializeConditionTests(unittest.TestCase):
    CLAUSE = "Validate untrusted input and use secure defaults."

    def condition(self, condition_id, task, repository):
        return {
            "id": condition_id,
            "task_security_clause": task,
            "repository_security_clause": repository,
        }

    def test_two_by_two_placement_uses_identical_clause(self):
        base = "Implement the requested function."
        task_prompt, task_file = MODULE.render_condition(base, self.CLAUSE, self.condition("task", True, False))
        repo_prompt, repo_file = MODULE.render_condition(base, self.CLAUSE, self.condition("repo", False, True))
        self.assertIn(self.CLAUSE, task_prompt)
        self.assertIsNone(task_file)
        self.assertNotIn(self.CLAUSE, repo_prompt)
        self.assertIn(self.CLAUSE, repo_file)
        self.assertEqual(task_prompt.count(self.CLAUSE), 1)
        self.assertEqual(repo_file.count(self.CLAUSE), 1)

    def test_both_condition_duplicates_only_location_not_wording(self):
        prompt, context = MODULE.render_condition(
            "Task",
            self.CLAUSE,
            self.condition("both", True, True),
        )
        self.assertIn(self.CLAUSE, prompt)
        self.assertIn(self.CLAUSE, context)

    def test_materialize_writes_only_repository_condition(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            record = MODULE.materialize(
                workspace,
                "Task",
                self.CLAUSE,
                self.condition("repo", False, True),
                "AGENTS.md",
            )
            self.assertTrue((workspace / "AGENTS.md").exists())
            self.assertEqual(record["security_clause_sha256"], MODULE.sha256_text(self.CLAUSE))
            self.assertIsNotNone(record["repository_context_sha256"])

    def test_refuses_to_overwrite_native_context(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            (workspace / "AGENTS.md").write_text("existing", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                MODULE.materialize(
                    workspace,
                    "Task",
                    self.CLAUSE,
                    self.condition("repo", False, True),
                    "AGENTS.md",
                )

    def test_config_has_complete_factorial(self):
        config_path = Path(__file__).parents[1] / "configs" / "conditions.json"
        config = json.loads(config_path.read_text(encoding="utf-8"))
        observed = {
            (item["task_security_clause"], item["repository_security_clause"])
            for item in config["conditions"]
        }
        self.assertEqual(observed, {(False, False), (True, False), (False, True), (True, True)})


if __name__ == "__main__":
    unittest.main()
