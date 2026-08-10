import copy
import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]
MODULE_PATH = ROOT / "scripts" / "analyze_factorial.py"
SPEC = importlib.util.spec_from_file_location("analyze_factorial", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class FactorialAnalysisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.design = json.loads(
            (ROOT / "configs" / "confirmatory_design.json").read_text()
        )

    def rows(self, design, control_security=False):
        rows = []
        for task in design["tasks"]:
            for condition in design["conditions"]:
                for repeat in range(1, design["repetitions_per_cell"] + 1):
                    secure = condition in {"task_only", "task_and_repository"}
                    if control_security and condition == "control":
                        secure = True
                    rows.append(
                        {
                            "task_id": task,
                            "condition": condition,
                            "repeat": str(repeat),
                            "functional_pass": "true",
                            "security_pass": str(secure).lower(),
                            "exit_state": "completed",
                            "pilot_only": "false",
                            "agent": "frozen-agent",
                        }
                    )
        return rows

    def test_recovers_task_instruction_effect(self):
        result = MODULE.analyze(self.rows(self.design), self.design)
        self.assertEqual(result["condition_joint_pass_rates"]["control"], 0.0)
        self.assertEqual(result["condition_joint_pass_rates"]["task_only"], 1.0)
        task_effect = result["contrasts"]["task_instruction_main_effect"]
        self.assertEqual(task_effect["estimate"], 1.0)
        self.assertAlmostEqual(task_effect["exact_sign_flip_p"], 2 / 256)
        self.assertEqual(
            result["contrasts"]["repository_instruction_main_effect"]["estimate"],
            0.0,
        )

    def test_refuses_pilot_record(self):
        rows = self.rows(self.design)
        rows[0]["pilot_only"] = "true"
        with self.assertRaisesRegex(ValueError, "refuses pilot-only"):
            MODULE.analyze(rows, self.design)

    def test_refuses_incomplete_matrix(self):
        rows = self.rows(self.design)
        rows.pop()
        with self.assertRaisesRegex(ValueError, "incomplete"):
            MODULE.analyze(rows, self.design)

    def test_refuses_multiple_agents(self):
        rows = self.rows(self.design)
        rows[0]["agent"] = "different-agent"
        with self.assertRaisesRegex(ValueError, "one frozen agent"):
            MODULE.analyze(rows, self.design)


if __name__ == "__main__":
    unittest.main()

