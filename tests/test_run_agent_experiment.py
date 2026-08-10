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

    def test_automatic_review_requires_explicit_mode(self):
        with tempfile.TemporaryDirectory() as directory:
            config = base_config()
            config["agents"]["codex_cli"]["arguments"].insert(-1, "--approve-for-me")
            path = self.write_config(directory, config)
            with self.assertRaisesRegex(ValueError, "approval_mode"):
                MODULE.load_frozen_agent(path, "codex_cli")

    def test_declared_automatic_review_is_accepted(self):
        with tempfile.TemporaryDirectory() as directory:
            config = base_config()
            agent = config["agents"]["codex_cli"]
            agent["arguments"].insert(-1, "--approve-for-me")
            agent["approval_mode"] = "automatic-review"
            path = self.write_config(directory, config)
            loaded = MODULE.load_frozen_agent(path, "codex_cli")
            self.assertEqual(loaded["approval_mode"], "automatic-review")

    def test_automatic_review_rejects_explicit_sandbox_combination(self):
        with tempfile.TemporaryDirectory() as directory:
            config = base_config()
            agent = config["agents"]["codex_cli"]
            agent["arguments"][-1:-1] = ["--approve-for-me", "--sandbox", "workspace-write"]
            agent["approval_mode"] = "automatic-review"
            path = self.write_config(directory, config)
            with self.assertRaisesRegex(ValueError, "cannot be combined"):
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

    def test_pilot_flag_is_available_and_recorded(self):
        source = MODULE_PATH.read_text(encoding="utf-8")
        self.assertIn('"--pilot-only"', source)
        self.assertIn('"pilot_only": args.pilot_only', source)

    def test_extracts_last_fenced_python_block(self):
        raw = "\n".join(
            [
                json.dumps({"item": {"type": "agent_message", "text": "checking"}}),
                json.dumps(
                    {
                        "item": {
                            "type": "agent_message",
                            "text": "```python\nvalue = 1\n```",
                        }
                    }
                ),
            ]
        )
        self.assertEqual(MODULE.extract_last_fenced_code(raw), "value = 1\n")

    def test_output_extraction_requires_code_block(self):
        with self.assertRaisesRegex(ValueError, "no non-empty"):
            MODULE.extract_last_fenced_code(
                json.dumps({"item": {"type": "agent_message", "text": "no code"}})
            )


if __name__ == "__main__":
    unittest.main()
