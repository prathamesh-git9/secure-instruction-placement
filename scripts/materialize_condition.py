#!/usr/bin/env python3
"""Materialize a wording-controlled instruction-placement condition."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


TASK_HEADER = "## Secure coding requirement"
REPOSITORY_HEADER = "# Repository secure-coding policy"


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def load_condition(config_path: Path, condition_id: str) -> tuple[str, dict]:
    config = json.loads(config_path.read_text(encoding="utf-8"))
    clause = config.get("security_clause")
    if not isinstance(clause, str) or not clause.strip():
        raise ValueError("conditions config has no non-empty security_clause")
    matches = [item for item in config.get("conditions", []) if item.get("id") == condition_id]
    if len(matches) != 1:
        raise ValueError(f"condition must resolve exactly once: {condition_id}")
    return clause.strip(), matches[0]


def render_condition(
    base_prompt: str,
    clause: str,
    condition: dict,
) -> tuple[str, str | None]:
    prompt = base_prompt.rstrip()
    repository_text: str | None = None
    if condition.get("task_security_clause") is True:
        prompt = f"{prompt}\n\n{TASK_HEADER}\n\n{clause}\n"
    else:
        prompt += "\n"
    if condition.get("repository_security_clause") is True:
        repository_text = f"{REPOSITORY_HEADER}\n\n{clause}\n"
    return prompt, repository_text


def materialize(
    workspace: Path,
    base_prompt: str,
    clause: str,
    condition: dict,
    context_filename: str,
) -> dict[str, object]:
    workspace.mkdir(parents=True, exist_ok=True)
    prompt, repository_text = render_condition(base_prompt, clause, condition)
    context_path = workspace / context_filename
    if context_path.exists():
        raise FileExistsError(f"refusing to overwrite existing context file: {context_path}")
    if repository_text is not None:
        context_path.write_text(repository_text, encoding="utf-8", newline="\n")
    return {
        "condition": condition["id"],
        "security_clause_sha256": sha256_text(clause),
        "prompt_sha256": sha256_text(prompt),
        "repository_context_sha256": sha256_text(repository_text) if repository_text is not None else None,
        "context_filename": context_filename if repository_text is not None else None,
        "prompt": prompt,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--condition", required=True)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--prompt-file", type=Path, required=True)
    parser.add_argument("--output-prompt", type=Path, required=True)
    parser.add_argument("--context-filename", default="AGENTS.md")
    args = parser.parse_args()
    clause, condition = load_condition(args.config, args.condition)
    base_prompt = args.prompt_file.read_text(encoding="utf-8")
    record = materialize(args.workspace, base_prompt, clause, condition, args.context_filename)
    args.output_prompt.write_text(str(record.pop("prompt")), encoding="utf-8", newline="\n")
    print(json.dumps(record, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

