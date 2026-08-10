#!/usr/bin/env python3
"""Validate development/holdout separation and the confirmatory design draft."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


EXPECTED_CONDITIONS = {
    "control",
    "task_only",
    "repository_only",
    "task_and_repository",
}


def validate(subset: dict, split: dict, design: dict) -> dict[str, int | str]:
    subset_tasks = subset.get("tasks", [])
    subset_ids = {task["task_id"] for task in subset_tasks}
    included_ids = {task["task_id"] for task in subset_tasks if task["status"] == "include"}
    excluded_ids = {task["task_id"] for task in subset_tasks if task["status"] == "exclude"}

    development = {item["task_id"] for item in split.get("development_tasks", [])}
    holdout = set(split.get("confirmatory_holdout_tasks", []))
    excluded = set(split.get("excluded_tasks", []))
    if development & holdout or development & excluded or holdout & excluded:
        raise ValueError("study split contains overlapping task groups")
    if development | holdout | excluded != subset_ids:
        raise ValueError("study split does not partition the audited subset")
    if development | holdout != included_ids:
        raise ValueError("development and holdout groups must equal included tasks")
    if excluded != excluded_ids:
        raise ValueError("split exclusions disagree with audited subset")

    task_by_id = {task["task_id"]: task for task in subset_tasks}
    families = {task_by_id[task_id]["weakness_family"] for task_id in holdout}
    if len(families) < 5:
        raise ValueError("confirmatory holdout must cover at least five weakness families")
    if set(design.get("tasks", [])) != holdout:
        raise ValueError("confirmatory design tasks disagree with locked holdout")
    if set(design.get("conditions", [])) != EXPECTED_CONDITIONS:
        raise ValueError("confirmatory design must contain the complete 2x2 condition set")
    repetitions = design.get("repetitions_per_cell")
    if not isinstance(repetitions, int) or repetitions < 2:
        raise ValueError("repetitions_per_cell must be an integer of at least two")
    planned = len(holdout) * len(EXPECTED_CONDITIONS) * repetitions
    if design.get("planned_runs_per_agent") != planned:
        raise ValueError("planned_runs_per_agent is inconsistent with the design")
    if design.get("analysis_unit") != "task":
        raise ValueError("confirmatory analysis must cluster at the task level")

    status = design.get("status")
    if status == "frozen":
        if design.get("independent_review_complete") is not True:
            raise ValueError("frozen design requires completed independent review")
        if not isinstance(design.get("agents"), list) or not design["agents"]:
            raise ValueError("frozen design requires at least one exact agent configuration")
        budget = design.get("budget_ceiling_usd")
        if not isinstance(budget, (int, float)) or budget <= 0:
            raise ValueError("frozen design requires a positive budget ceiling")
    elif status != "draft-awaiting-review-and-budget":
        raise ValueError(f"unrecognized design status: {status!r}")

    return {
        "status": status,
        "development_tasks": len(development),
        "holdout_tasks": len(holdout),
        "excluded_tasks": len(excluded),
        "holdout_families": len(families),
        "planned_runs_per_agent": planned,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--subset", type=Path, required=True)
    parser.add_argument("--split", type=Path, required=True)
    parser.add_argument("--design", type=Path, required=True)
    args = parser.parse_args()
    subset = json.loads(args.subset.read_text(encoding="utf-8"))
    split = json.loads(args.split.read_text(encoding="utf-8"))
    design = json.loads(args.design.read_text(encoding="utf-8"))
    print(json.dumps(validate(subset, split, design), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

