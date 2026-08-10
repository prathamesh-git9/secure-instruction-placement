#!/usr/bin/env python3
"""Generate or validate the blocked, randomized confirmatory run schedule."""

from __future__ import annotations

import argparse
import csv
import json
import random
from pathlib import Path


FIELDS = ("run_index", "block", "task_id", "condition", "repeat", "run_id")


def build_rows(design: dict) -> list[dict[str, str | int]]:
    rng = random.Random(design["run_order"]["seed"])
    tasks = list(design["tasks"])
    conditions = list(design["conditions"])
    rows: list[dict[str, str | int]] = []
    run_index = 1
    for repeat in range(1, design["repetitions_per_cell"] + 1):
        block = [
            {"task_id": task, "condition": condition}
            for task in tasks
            for condition in conditions
        ]
        rng.shuffle(block)
        for cell in block:
            rows.append(
                {
                    "run_index": run_index,
                    "block": repeat,
                    "task_id": cell["task_id"],
                    "condition": cell["condition"],
                    "repeat": repeat,
                    "run_id": (
                        f'confirmatory-v1-r{repeat:02d}-'
                        f'{cell["task_id"]}-{cell["condition"]}'
                    ),
                }
            )
            run_index += 1
    return rows


def validate_rows(rows: list[dict[str, str]], design: dict) -> dict[str, int]:
    expected_cells = {
        (task, condition)
        for task in design["tasks"]
        for condition in design["conditions"]
    }
    expected_total = len(expected_cells) * design["repetitions_per_cell"]
    if len(rows) != expected_total:
        raise ValueError(f"schedule has {len(rows)} rows; expected {expected_total}")
    indices = [int(row["run_index"]) for row in rows]
    if indices != list(range(1, expected_total + 1)):
        raise ValueError("run_index must be unique, ordered, and contiguous")
    run_ids = [row["run_id"] for row in rows]
    if len(run_ids) != len(set(run_ids)):
        raise ValueError("run_id values must be unique")
    for repeat in range(1, design["repetitions_per_cell"] + 1):
        block_rows = [row for row in rows if int(row["block"]) == repeat]
        cells = {(row["task_id"], row["condition"]) for row in block_rows}
        if cells != expected_cells or any(int(row["repeat"]) != repeat for row in block_rows):
            raise ValueError(f"block {repeat} is not a complete task-condition matrix")
    return {
        "runs": len(rows),
        "blocks": design["repetitions_per_cell"],
        "tasks": len(design["tasks"]),
        "conditions": len(design["conditions"]),
    }


def write_schedule(design: dict, output: Path) -> dict[str, int]:
    if output.exists():
        raise ValueError(f"refusing to overwrite schedule: {output}")
    rows = build_rows(design)
    with output.open("x", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    return validate_rows([{key: str(value) for key, value in row.items()} for row in rows], design)


def read_schedule(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--design", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--validate-existing", action="store_true")
    args = parser.parse_args()
    design = json.loads(args.design.read_text(encoding="utf-8"))
    if args.validate_existing:
        result = validate_rows(read_schedule(args.output), design)
    else:
        result = write_schedule(design, args.output)
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

