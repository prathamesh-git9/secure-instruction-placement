#!/usr/bin/env python3
"""Validate and publish the fixed three-task writable-agent pilot matrix."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
from pathlib import Path


TASKS = (
    "DeserializationPyYAML",
    "CommandInjectionSubprocessRun",
    "CodeInjectionEval",
)
CONDITIONS = ("control", "task_only", "repository_only", "task_and_repository")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_record(record: dict, task: str, condition: str, source: Path) -> None:
    if record.get("task_id") != task or record.get("condition") != condition:
        raise ValueError(f"record identity mismatch for {task}/{condition}")
    if record.get("pilot_only") is not True:
        raise ValueError(f"record is not pilot-only: {task}/{condition}")
    if record.get("output_extracted") is not False:
        raise ValueError(f"record is not a writable-agent run: {task}/{condition}")
    if not source.is_file():
        raise ValueError(f"target source is missing: {task}/{condition}")
    actual = sha256_file(source)
    if record.get("artifact_hash") != actual:
        raise ValueError(f"artifact hash mismatch: {task}/{condition}")


def collect(pilots: Path, output: Path) -> dict[str, int]:
    if output.exists():
        raise ValueError(f"refusing to overwrite output: {output}")
    generated = output / "generated"
    records = output / "records"
    generated.mkdir(parents=True)
    records.mkdir()
    rows: list[dict[str, object]] = []
    manifest: list[str] = []

    for task in TASKS:
        for condition in CONDITIONS:
            run = pilots / f"2026-08-10-writable-{task}-{condition}"
            record_path = run / "artifact" / "record.json"
            record = json.loads(record_path.read_text(encoding="utf-8"))
            source = run / "workspace" / Path(str(record["target_path"]))
            validate_record(record, task, condition, source)
            stem = f"{task}__{condition}"
            public_source = generated / f"{stem}.py"
            public_record = records / f"{stem}.json"
            shutil.copyfile(source, public_source)
            shutil.copyfile(record_path, public_record)
            counts = record["verifier_counts"]
            rows.append(
                {
                    "task": task,
                    "condition": condition,
                    "functional_pass": record["functional_pass"],
                    "functional_passed_tests": counts["functional_total"]
                    - counts["functional_failed"],
                    "functional_total": counts["functional_total"],
                    "security_pass": record["security_pass"],
                    "security_passed_tests": counts["security_total"]
                    - counts["security_failed"],
                    "security_total": counts["security_total"],
                    "input_tokens": record["input_tokens"],
                    "output_tokens": record["output_tokens"],
                    "wall_seconds": f'{record["wall_seconds"]:.6f}',
                    "artifact_sha256": record["artifact_hash"],
                }
            )
            manifest.append(f'{record["artifact_hash"]}  generated/{public_source.name}')

    with (output / "summary.csv").open("x", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    (output / "manifest.sha256").write_text(
        "\n".join(manifest) + "\n", encoding="utf-8", newline="\n"
    )
    return {
        "runs": len(rows),
        "functional_pass": sum(row["functional_pass"] is True for row in rows),
        "security_pass": sum(row["security_pass"] is True for row in rows),
    }


def validate_public(output: Path) -> dict[str, int]:
    runs = 0
    functional_pass = 0
    security_pass = 0
    for task in TASKS:
        for condition in CONDITIONS:
            stem = f"{task}__{condition}"
            record = json.loads(
                (output / "records" / f"{stem}.json").read_text(encoding="utf-8")
            )
            source = output / "generated" / f"{stem}.py"
            validate_record(record, task, condition, source)
            runs += 1
            functional_pass += record.get("functional_pass") is True
            security_pass += record.get("security_pass") is True
    return {
        "runs": runs,
        "functional_pass": functional_pass,
        "security_pass": security_pass,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilots", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--validate-existing", action="store_true")
    args = parser.parse_args()
    if args.validate_existing:
        result = validate_public(args.output)
    else:
        if args.pilots is None:
            parser.error("--pilots is required unless --validate-existing is used")
        result = collect(args.pilots, args.output)
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
