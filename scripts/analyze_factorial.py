#!/usr/bin/env python3
"""Analyze a balanced 2x2 coding-agent experiment at the task-cluster level."""

from __future__ import annotations

import argparse
import csv
import itertools
import json
import random
from collections import defaultdict
from pathlib import Path


CONTRASTS = {
    "task_instruction_main_effect": {
        "control": -0.5,
        "task_only": 0.5,
        "repository_only": -0.5,
        "task_and_repository": 0.5,
    },
    "repository_instruction_main_effect": {
        "control": -0.5,
        "task_only": -0.5,
        "repository_only": 0.5,
        "task_and_repository": 0.5,
    },
    "task_by_repository_interaction": {
        "control": 1.0,
        "task_only": -1.0,
        "repository_only": -1.0,
        "task_and_repository": 1.0,
    },
    "task_only_minus_control": {"control": -1.0, "task_only": 1.0},
    "repository_only_minus_control": {"control": -1.0, "repository_only": 1.0},
    "both_minus_control": {"control": -1.0, "task_and_repository": 1.0},
}


def parse_bool(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized in {"true", "1", "yes"}:
        return True
    if normalized in {"false", "0", "no"}:
        return False
    raise ValueError(f"invalid boolean value: {value!r}")


def quantile(values: list[float], probability: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    fraction = position - lower
    return ordered[lower] * (1 - fraction) + ordered[upper] * fraction


def exact_sign_flip_p(values: list[float]) -> float:
    observed = abs(sum(values) / len(values))
    extreme = 0
    total = 0
    for signs in itertools.product((-1.0, 1.0), repeat=len(values)):
        candidate = abs(sum(sign * value for sign, value in zip(signs, values)) / len(values))
        extreme += candidate >= observed - 1e-12
        total += 1
    return extreme / total


def bootstrap_interval(
    values: list[float], resamples: int, seed: int, confidence_level: float
) -> tuple[float, float]:
    rng = random.Random(seed)
    n = len(values)
    estimates = [
        sum(values[rng.randrange(n)] for _ in range(n)) / n for _ in range(resamples)
    ]
    alpha = 1.0 - confidence_level
    return quantile(estimates, alpha / 2), quantile(estimates, 1 - alpha / 2)


def analyze(rows: list[dict[str, str]], design: dict) -> dict:
    tasks = list(design["tasks"])
    conditions = list(design["conditions"])
    repetitions = design["repetitions_per_cell"]
    expected = {
        (task, condition, repeat)
        for task in tasks
        for condition in conditions
        for repeat in range(1, repetitions + 1)
    }
    observed: dict[tuple[str, str, int], float] = {}
    agents: set[str] = set()
    for row in rows:
        required = {
            "task_id",
            "condition",
            "repeat",
            "functional_pass",
            "security_pass",
            "exit_state",
            "pilot_only",
        }
        missing = required - set(row)
        if missing:
            raise ValueError(f"result row is missing fields: {', '.join(sorted(missing))}")
        if parse_bool(row["pilot_only"]):
            raise ValueError("confirmatory analysis refuses pilot-only records")
        key = (row["task_id"], row["condition"], int(row["repeat"]))
        if key not in expected:
            raise ValueError(f"unexpected result cell: {key}")
        if key in observed:
            raise ValueError(f"duplicate result cell: {key}")
        joint = (
            row["exit_state"] == "completed"
            and parse_bool(row["functional_pass"])
            and parse_bool(row["security_pass"])
        )
        observed[key] = float(joint)
        if row.get("agent"):
            agents.add(row["agent"])
    missing_cells = expected - set(observed)
    if missing_cells:
        raise ValueError(f"balanced matrix is incomplete: {len(missing_cells)} cells missing")
    if len(agents) > 1:
        raise ValueError("analyze one frozen agent configuration at a time")

    task_condition: dict[str, dict[str, float]] = defaultdict(dict)
    for task in tasks:
        for condition in conditions:
            values = [observed[(task, condition, repeat)] for repeat in range(1, repetitions + 1)]
            task_condition[task][condition] = sum(values) / repetitions

    condition_rates = {
        condition: sum(task_condition[task][condition] for task in tasks) / len(tasks)
        for condition in conditions
    }
    uncertainty = design["uncertainty"]
    contrast_results = {}
    for index, (name, coefficients) in enumerate(CONTRASTS.items()):
        task_effects = [
            sum(coefficients.get(condition, 0.0) * task_condition[task][condition] for condition in conditions)
            for task in tasks
        ]
        estimate = sum(task_effects) / len(task_effects)
        lower, upper = bootstrap_interval(
            task_effects,
            uncertainty["bootstrap_resamples"],
            uncertainty["bootstrap_seed"] + index,
            uncertainty["confidence_level"],
        )
        contrast_results[name] = {
            "estimate": estimate,
            "confidence_interval": [lower, upper],
            "exact_sign_flip_p": exact_sign_flip_p(task_effects),
            "task_effects": dict(zip(tasks, task_effects)),
        }

    return {
        "design_id": design["design_id"],
        "agent": next(iter(agents), None),
        "task_count": len(tasks),
        "run_count": len(rows),
        "primary_outcome": design["primary_outcome"],
        "condition_joint_pass_rates": condition_rates,
        "contrasts": contrast_results,
        "warning": "Task count is small; intervals and exact tests are primary, and estimates must not be generalized beyond the frozen tasks and agent.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--design", type=Path, required=True)
    parser.add_argument("--results", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    design = json.loads(args.design.read_text(encoding="utf-8"))
    with args.results.open(encoding="utf-8", newline="") as handle:
        result = analyze(list(csv.DictReader(handle)), design)
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8", newline="\n")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

