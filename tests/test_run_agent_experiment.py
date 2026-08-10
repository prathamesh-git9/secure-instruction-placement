import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).parents[1] / "scripts" / "run_agent_experiment.py"
sys.path.insert(0, str(MODULE_PATH.parent))
SPEC = importlib.util.spec_from_file_location("run_agent_experiment", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


def base_config(status="frozen"):
    return {
        "status": status,
        "agents": {
            "codex_cli": {
                "binary": "codex",
                "observed_version": "codex-cli 0.147.0",
                "context_filename": "AGENTS.md",
                "prompt_transport": "stdin",
                "arguments": ["exec", "--ephemeral", "--json", "-"],
                "model": "model-under-test",
                "reasoning_effort": "high",
            }
        },
    }


class AgentExperimentTests(unittest.TestCase):
    def write_config(self, directory, value):
        path = Path(directory) / "agents.json"
        path.write_text(json.dumps(value), encoding="utf-8")
        return path

    def test_draft_config_refuses_model_run(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.write_config(directory, base_config("draft-not-frozen"))
            with self.assertRaisesRegex(ValueError, "not frozen"):
                MODULE.load_frozen_agent(path, "codex_cli")

    def test_forbidden_bypass_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            config = base_config()
            config["agents"]["codex_cli"]["arguments"].insert(
                -1, "--dangerously-bypass-approvals-and-sandbox"
            )
            path = self.write_config(directory, config)
            with self.assertRaisesRegex(ValueError, "forbidden"):
                MODULE.load_frozen_agent(path, "codex_cli")

    def test_model_and_reasoning_are_explicit_in_command(self):
        agent = base_config()["agents"]["codex_cli"]
        command = MODULE.build_command(agent)
        self.assertEqual(command[-1], "-")
        self.assertIn("model-under-test", command)
        self.assertIn('model_reasoning_effort="high"', command)

    def test_usage_parser_uses_largest_reported_totals(self):
        raw = "\n".join(
            [
                json.dumps({"usage": {"input_tokens": 10, "output_tokens": 3}}),
                "not-json",
                json.dumps({"usage": {"input_tokens": 25, "output_tokens": 8}}),
            ]
        )
        self.assertEqual(MODULE.parse_jsonl_usage(raw), (25, 8))


if __name__ == "__main__":
    unittest.main()
