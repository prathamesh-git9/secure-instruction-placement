#!/usr/bin/env python3
"""Exercise one SecCodeBench task without invoking a model.

This is an infrastructure pilot, not an experimental observation. It places a
supplied source file in the task workspace, materializes one instruction
condition, calls the pinned local verifier, and writes one immutable JSON
record.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from urllib.parse import urlparse

from audit_seeded_baselines import local_endpoint, parse_counts, post_code
from materialize_condition import load_condition, materialize


OUTPUT_TARGET = re.compile(
    r"Output\s+the\s+complete\s+code\s+for\s+`([^`]+)`",
    flags=re.IGNORECASE,
)
OUTPUT_SECTION = re.compile(r"\n##\s+Output(?:\s+Format)?\s*\n", flags=re.IGNORECASE)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def prompt_target(prompt: str) -> PurePosixPath:
    matches = OUTPUT_TARGET.findall(prompt)
    if len(matches) != 1:
        raise ValueError(f"expected one declared output target, found {len(matches)}")
    target = PurePosixPath(matches[0])
    if target.is_absolute() or ".." in target.parts:
        raise ValueError(f"unsafe output target: {target}")
    return target


def verifier_repository(upstream: Path, verify_url: str) -> Path:
    parts = urlparse(verify_url).path.strip("/").split("/")
    if len(parts) != 3 or parts[0] != "verify":
        raise ValueError(f"unrecognized verifier URL: {verify_url}")
    return upstream / "docker" / "model" / "python" / "python_bench" / parts[1] / parts[2]


def signature_target(repository: Path) -> PurePosixPath:
    signature = json.loads((repository / "signature.json").read_text(encoding="utf-8"))
    module = signature.get("module_name")
    if not isinstance(module, str) or not module or "/" in module or "\\" in module:
        raise ValueError(f"invalid Python module_name in {repository / 'signature.json'}")
    return PurePosixPath("src") / module / f"{module}.py"


def normalize_prompt(prompt: str, target: PurePosixPath) -> str:
    match = OUTPUT_SECTION.search(prompt)
    body = prompt[: match.start()].rstrip() if match else prompt.rstrip()
    return (
        f"{body}\n\n## Output format\n\n"
        f"Write the complete implementation to `{target.as_posix()}`. "
        "Do not only describe the change.\n"
    )


def load_task(upstream: Path, task_id: str) -> dict[str, object]:
    benchmark_file = upstream / "datasets" / "benchmark" / "python" / "python.json"
    benchmark = json.loads(benchmark_file.read_text(encoding="utf-8"))
    if task_id not in benchmark:
        raise ValueError(f"unknown Python task: {task_id}")
    metadata = benchmark[task_id]
    prompt_file = (
        upstream
        / "datasets"
        / "benchmark"
        / "python"
        / "prompts"
        / f"{metadata['prompt']}.en-US"
    )
    prompt = prompt_file.read_text(encoding="utf-8")
    verify_url = metadata["verify_urls"]["gen"]
    repository = verifier_repository(upstream, verify_url)
    declared_target = prompt_target(prompt)
    expected_target = signature_target(repository)
    if declared_target != expected_target:
        raise ValueError(
            f"prompt/verifier target disagreement for {task_id}: "
            f"{declared_target} != {expected_target}"
        )
    params_targets = sorted(str(PurePosixPath(path)) for path in metadata.get("params", {}).values())
    return {
        "metadata": metadata,
        "prompt": normalize_prompt(prompt, expected_target),
        "prompt_file": prompt_file,
        "verify_url": verify_url,
        "repository": repository,
        "target": expected_target,
        "metadata_target_mismatch": expected_target.as_posix() not in params_targets,
        "metadata_targets": params_targets,
    }


def write_exclusive_json(path: Path, record: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(record, handle, indent=2, sort_keys=True)
        handle.write("\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--upstream", type=Path, required=True)
    parser.add_argument("--task", required=True)
    parser.add_argument("--condition", required=True)
    parser.add_argument("--conditions", type=Path, required=True)
    parser.add_argument("--source-file", type=Path, required=True)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--record", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--endpoint", default="http://localhost:24684")
    parser.add_argument("--timeout", type=int, default=180)
    args = parser.parse_args()

    upstream = args.upstream.resolve()
    workspace = args.workspace.resolve()
    if workspace.exists():
        raise SystemExit(f"refusing to reuse workspace: {workspace}")
    task = load_task(upstream, args.task)
    clause, condition = load_condition(args.conditions.resolve(), args.condition)
    condition_record = materialize(
        workspace,
        str(task["prompt"]),
        clause,
        condition,
        "AGENTS.md",
    )
    rendered_prompt = str(condition_record.pop("prompt"))
    harness_dir = workspace / ".experiment"
    harness_dir.mkdir(parents=True, exist_ok=False)
    (harness_dir / "prompt.txt").write_text(rendered_prompt, encoding="utf-8", newline="\n")

    source = args.source_file.resolve().read_bytes()
    target = workspace.joinpath(*task["target"].parts)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(source)

    started_at = datetime.now(timezone.utc)
    start = time.monotonic()
    result = post_code(
        local_endpoint(str(task["verify_url"]), args.endpoint),
        source.decode("utf-8"),
        args.timeout,
    )
    wall_seconds = time.monotonic() - start
    counts = parse_counts(result)
    record = {
        "run_id": args.run_id,
        "task_id": args.task,
        "condition": args.condition,
        "agent": "supplied-source-pilot",
        "agent_version": "not-applicable",
        "model": "not-applicable",
        "started_at": started_at.isoformat(),
        "seed": None,
        "functional_pass": counts["functional_failed"] == 0,
        "security_pass": counts["security_failed"] == 0,
        "input_tokens": None,
        "output_tokens": None,
        "cost_usd": 0.0,
        "wall_seconds": wall_seconds,
        "exit_state": "completed",
        "artifact_hash": sha256_bytes(source),
        "notes": "Infrastructure-only supplied-source pilot; exclude from experiment.",
        "pilot_only": True,
        "upstream_revision": "67126efb88c6dd75f1fb4963048cab2f7b23d83d",
        "target_path": task["target"].as_posix(),
        "metadata_target_mismatch": task["metadata_target_mismatch"],
        "metadata_targets": task["metadata_targets"],
        "condition_materialization": condition_record,
        "verifier_counts": counts,
    }
    write_exclusive_json(args.record.resolve(), record)
    json.dump(record, sys.stdout, sort_keys=True)
    sys.stdout.write("\n")
    return 0 if record["functional_pass"] and record["security_pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
