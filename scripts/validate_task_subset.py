#!/usr/bin/env python3
"""Validate the audited task-subset decision file."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def validate(value: dict) -> dict[str, int]:
    source = value.get("source")
    if not isinstance(source, dict) or not source.get("revision"):
        raise ValueError("source revision is required")
    tasks = value.get("tasks")
    if not isinstance(tasks, list) or not tasks:
        raise ValueError("tasks must be a non-empty list")

    ids: set[str] = set()
    included = 0
    excluded = 0
    families: set[str] = set()
    for index, task in enumerate(tasks):
        if not isinstance(task, dict):
            raise ValueError(f"task {index} is not an object")
        task_id = task.get("task_id")
        if not isinstance(task_id, str) or not task_id:
            raise ValueError(f"task {index} has no task_id")
        if task_id in ids:
            raise ValueError(f"duplicate task_id: {task_id}")
        ids.add(task_id)
        status = task.get("status")
        if status == "include":
            included += 1
            if task.get("functional_failed") != 0:
                raise ValueError(f"included task fails functional baseline: {task_id}")
            if task.get("seed_detected") is not True or task.get("security_failed", 0) < 1:
                raise ValueError(f"included task has no detected vulnerable seed: {task_id}")
            family = task.get("weakness_family")
            if not isinstance(family, str) or not family:
                raise ValueError(f"included task has no weakness family: {task_id}")
            families.add(family)
        elif status == "exclude":
            excluded += 1
            if not isinstance(task.get("exclusion_reason"), str) or not task["exclusion_reason"].strip():
                raise ValueError(f"excluded task has no reason: {task_id}")
        else:
            raise ValueError(f"invalid status for {task_id}: {status!r}")

        for field in ("functional_failed", "functional_total", "security_failed", "security_total"):
            count = task.get(field)
            if not isinstance(count, int) or count < 0:
                raise ValueError(f"invalid {field} for {task_id}")

    if len(families) < 5:
        raise ValueError("included subset must cover at least five weakness families")
    return {
        "total": len(tasks),
        "included": included,
        "excluded": excluded,
        "weakness_families": len(families),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("config", type=Path)
    args = parser.parse_args()
    value = json.loads(args.config.read_text(encoding="utf-8"))
    print(json.dumps(validate(value), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

