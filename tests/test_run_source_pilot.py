import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path, PurePosixPath


MODULE_PATH = Path(__file__).parents[1] / "scripts" / "run_source_pilot.py"
sys.path.insert(0, str(MODULE_PATH.parent))
SPEC = importlib.util.spec_from_file_location("run_source_pilot", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class SourcePilotTests(unittest.TestCase):
    def test_prompt_target_extracts_safe_relative_path(self):
        prompt = "Task\n\n## Output\nOutput the complete code for `src/demo/demo.py`."
        self.assertEqual(MODULE.prompt_target(prompt), PurePosixPath("src/demo/demo.py"))

    def test_prompt_target_rejects_traversal(self):
        with self.assertRaises(ValueError):
            MODULE.prompt_target("Output the complete code for `../escape.py`.")

    def test_signature_target_uses_verifier_contract(self):
        with tempfile.TemporaryDirectory() as directory:
            repository = Path(directory)
            (repository / "signature.json").write_text(
                json.dumps({"module_name": "workspace_state_manager"}),
                encoding="utf-8",
            )
            self.assertEqual(
                MODULE.signature_target(repository),
                PurePosixPath("src/workspace_state_manager/workspace_state_manager.py"),
            )

    def test_normalize_prompt_replaces_xml_output_section(self):
        prompt = "Implement it.\n\n## Output\nOld XML directions"
        rendered = MODULE.normalize_prompt(prompt, PurePosixPath("src/demo.py"))
        self.assertNotIn("Old XML", rendered)
        self.assertIn("`src/demo.py`", rendered)

    def test_write_exclusive_json_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "record.json"
            MODULE.write_exclusive_json(path, {"first": True})
            with self.assertRaises(FileExistsError):
                MODULE.write_exclusive_json(path, {"first": False})


if __name__ == "__main__":
    unittest.main()
