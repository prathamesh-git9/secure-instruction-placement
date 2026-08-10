#!/usr/bin/env python3
"""Run one frozen coding-agent experiment and preserve its raw evidence.

The runner intentionally refuses draft agent configuration. It is safe to build
and test now, but cannot spend model budget until the model, reasoning setting,
version, and overall configuration are explicitly frozen.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from audit_seeded_baselines import local_endpoint, parse_counts, post_code
from materialize_condition import load_condition, materialize
from run_source_pilot import load_task, sha256_bytes, write_exclusive_json


FORBIDDEN_ARGUMENTS = {
    "--dangerously-bypass-approvals-and-sandbox",
    "--dangerously-bypass-hook-trust",
    "--approve-for-me",
}
REASONING_LEVELS = {"low", "medium", "high", "xhigh", "max", "ultra"}


def load_frozen_agent(config_path: Path, agent_id: str) -> dict[str, object]:
    config = json.loads(config_path.read_text(encoding="utf-8"))
    if config.get("status") != "frozen":
        raise ValueError("agent configuration is not frozen; refusing a model run")
    agents = config.get("agents", {})
    if agent_id not in agents:
        raise ValueError(f"unknown agent: {agent_id}")
    agent = agents[agent_id]
    arguments = agent.get("arguments")
    if not isinstance(arguments, list) or not all(isinstance(value, str) for value in arguments):
        raise ValueError("agent arguments must be a list of strings")
    forbidden = FORBIDDEN_ARGUMENTS.intersection(arguments)
    if forbidden:
        raise ValueError(f"forbidden agent argument(s): {', '.join(sorted(forbidden))}")
    if agent.get("prompt_transport") != "stdin" or arguments[-1:] != ["-"]:
        raise ValueError("runner requires stdin prompt transport ending in '-' argument")
    if agent.get("context_filename") not in {"AGENTS.md", "CLAUDE.md"}:
        raise ValueError("unsupported native context filename")
    model = agent.get("model")
    reasoning = agent.get("reasoning_effort")
    if not isinstance(model, str) or not model.strip():
        raise ValueError("model must be explicitly frozen")
    if reasoning not in REASONING_LEVELS:
        raise ValueError("reasoning_effort must be explicitly frozen")
    return agent


def build_command(agent: dict[str, object]) -> list[str]:
    binary = agent.get("binary")
    if not isinstance(binary, str) or not binary:
        raise ValueError("agent binary is missing")
    arguments = list(agent["arguments"])
    terminal_prompt = arguments.pop()
    return [
        binary,
        *arguments,
        "--model",
        str(agent["model"]),
        "--config",
        f'model_reasoning_effort="{agent["reasoning_effort"]}"',
        terminal_prompt,
    ]


def check_version(agent: dict[str, object], timeout: int = 15) -> str:
    completed = subprocess.run(
        [str(agent["binary"]), "--version"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        check=False,
    )
    observed = completed.stdout.strip() or completed.stderr.strip()
    expected = agent.get("observed_version")
    if completed.returncode != 0 or observed != expected:
        raise ValueError(f"agent version drift: expected {expected!r}, observed {observed!r}")
    return observed


def parse_jsonl_usage(raw: str) -> tuple[int | None, int | None]:
    input_values: list[int] = []
    output_values: list[int] = []

    def visit(value: object) -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                if key in {"input_tokens", "input_token_count"} and isinstance(child, int):
                    input_values.append(child)
                if key in {"output_tokens", "output_token_count"} and isinstance(child, int):
                    output_values.append(child)
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)

    for line in raw.splitlines():
        try:
            visit(json.loads(line))
        except json.JSONDecodeError:
            continue
    return (max(input_values) if input_values else None, max(output_values) if output_values else None)


def write_exclusive_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(value)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--upstream", type=Path, required=True)
    parser.add_argument("--task", required=True)
    parser.add_argument("--condition", required=True)
    parser.add_argument("--conditions", type=Path, required=True)
    parser.add_argument("--agent-config", type=Path, required=True)
    parser.add_argument("--agent", required=True)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--artifact-dir", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--endpoint", default="http://localhost:24684")
    parser.add_argument("--agent-timeout", type=int, default=900)
    parser.add_argument("--verifier-timeout", type=int, default=180)
    args = parser.parse_args()

    upstream = args.upstream.resolve()
    workspace = args.workspace.resolve()
    artifact_dir = args.artifact_dir.resolve()
    if workspace.exists():
        raise SystemExit(f"refusing to reuse workspace: {workspace}")
    if artifact_dir.exists():
        raise SystemExit(f"refusing to reuse artifact directory: {artifact_dir}")

    try:
        agent = load_frozen_agent(args.agent_config.resolve(), args.agent)
        version = check_version(agent)
    except ValueError as exc:
        raise SystemExit(str(exc)) from None
    task = load_task(upstream, args.task)
    clause, condition = load_condition(args.conditions.resolve(), args.condition)
    condition_record = materialize(
        workspace,
        str(task["prompt"]),
        clause,
        condition,
        str(agent["context_filename"]),
    )
    prompt = str(condition_record.pop("prompt"))
    command = build_command(agent)
    started_at = datetime.now(timezone.utc)
    start = time.monotonic()
    exit_state = "completed"
    exit_code: int | None = None
    stdout = ""
    stderr = ""
    try:
        completed = subprocess.run(
            command,
            cwd=workspace,
            input=prompt,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=args.agent_timeout,
            check=False,
        )
        exit_code = completed.returncode
        stdout = completed.stdout
        stderr = completed.stderr
        if exit_code != 0:
            exit_state = "agent_error"
    except subprocess.TimeoutExpired as exc:
        exit_state = "timeout"
        stdout = exc.stdout if isinstance(exc.stdout, str) else ""
        stderr = exc.stderr if isinstance(exc.stderr, str) else ""
    wall_seconds = time.monotonic() - start

    target = workspace.joinpath(*task["target"].parts)
    source = target.read_bytes() if target.is_file() else b""
    functional_pass = False
    security_pass = False
    counts: dict[str, int | bool] | None = None
    if exit_state == "completed" and source:
        try:
            result = post_code(
                local_endpoint(str(task["verify_url"]), args.endpoint),
                source.decode("utf-8"),
                args.verifier_timeout,
            )
            counts = parse_counts(result)
            functional_pass = counts["functional_failed"] == 0
            security_pass = counts["security_failed"] == 0
        except Exception as exc:  # preserve the run even when infrastructure fails
            exit_state = "harness_error"
            stderr += f"\nVerifier error: {type(exc).__name__}: {exc}\n"

    input_tokens, output_tokens = parse_jsonl_usage(stdout)
    record = {
        "run_id": args.run_id,
        "task_id": args.task,
        "condition": args.condition,
        "agent": args.agent,
        "agent_version": version,
        "model": agent["model"],
        "started_at": started_at.isoformat(),
        "seed": None,
        "functional_pass": functional_pass,
        "security_pass": security_pass,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "cost_usd": None,
        "wall_seconds": wall_seconds,
        "exit_state": exit_state,
        "artifact_hash": sha256_bytes(source),
        "notes": "Frozen-agent experimental run; inspect raw logs and diff before inclusion.",
        "pilot_only": False,
        "upstream_revision": "67126efb88c6dd75f1fb4963048cab2f7b23d83d",
        "target_path": task["target"].as_posix(),
        "metadata_target_mismatch": task["metadata_target_mismatch"],
        "metadata_targets": task["metadata_targets"],
        "condition_materialization": condition_record,
        "verifier_counts": counts or {},
        "agent_exit_code": exit_code,
        "command": command,
        "stdout_sha256": sha256_bytes(stdout.encode("utf-8")),
        "stderr_sha256": sha256_bytes(stderr.encode("utf-8")),
    }
    artifact_dir.mkdir(parents=True, exist_ok=False)
    write_exclusive_text(artifact_dir / "agent.jsonl", stdout)
    write_exclusive_text(artifact_dir / "agent.stderr.txt", stderr)
    write_exclusive_text(artifact_dir / "prompt.txt", prompt)
    write_exclusive_json(artifact_dir / "record.json", record)
    json.dump(record, sys.stdout, sort_keys=True)
    sys.stdout.write("\n")
    return 0 if exit_state == "completed" else 2


if __name__ == "__main__":
    raise SystemExit(main())
