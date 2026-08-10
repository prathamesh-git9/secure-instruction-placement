#!/usr/bin/env python3
"""Summarise functional and security outcomes from append-only run CSV data."""

from __future__ import annotations

import argparse
import csv
import math
from collections import defaultdict
from pathlib import Path


TRUE_VALUES = {"1", "true", "yes", "y"}
FALSE_VALUES = {"0", "false", "no", "n"}
REQUIRED_COLUMNS = {"condition", "agent", "task_id", "functional_pass", "security_pass"}


def parse_bool(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized in TRUE_VALUES:
        return True
    if normalized in FALSE_VALUES:
        return False
    raise ValueError(f"invalid boolean value: {value!r}")


def wilson_interval(successes: int, total: int, z: float = 1.959963984540054) -> tuple[float, float]:
    if total == 0:
        return math.nan, math.nan
    p = successes / total
    denominator = 1 + z * z / total
    center = (p + z * z / (2 * total)) / denominator
    margin = z * math.sqrt((p * (1 - p) + z * z / (4 * total)) / total) / denominator
    return max(0.0, center - margin), min(1.0, center + margin)


def load_rows(path: Path) -> list[dict[str, object]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        fieldnames = set(reader.fieldnames or [])
        missing = REQUIRED_COLUMNS - fieldnames
        if missing:
            raise ValueError(f"missing columns: {', '.join(sorted(missing))}")
        rows: list[dict[str, object]] = []
        for line_number, row in enumerate(reader, start=2):
            try:
                functional = parse_bool(row["functional_pass"])
                security = parse_bool(row["security_pass"])
            except ValueError as exc:
                raise ValueError(f"line {line_number}: {exc}") from exc
            rows.append({**row, "functional_pass": functional, "security_pass": security})
    return rows


def summarise(rows: list[dict[str, object]], group_by: list[str]) -> list[dict[str, object]]:
    grouped: dict[tuple[object, ...], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        grouped[tuple(row.get(key, "") for key in group_by)].append(row)

    output: list[dict[str, object]] = []
    for key, group in sorted(grouped.items(), key=lambda item: tuple(map(str, item[0]))):
        total = len(group)
        functional = sum(bool(row["functional_pass"]) for row in group)
        security = sum(bool(row["security_pass"]) for row in group)
        secure_and_correct = sum(bool(row["functional_pass"]) and bool(row["security_pass"]) for row in group)
        vulnerable_among_correct = functional - secure_and_correct
        low, high = wilson_interval(secure_and_correct, total)
        record: dict[str, object] = dict(zip(group_by, key, strict=True))
        record.update(
            n=total,
            functional_pass=functional,
            functional_rate=functional / total,
            security_pass=security,
            security_rate=security / total,
            secure_and_correct=secure_and_correct,
            secure_and_correct_rate=secure_and_correct / total,
            secure_and_correct_ci_low=low,
            secure_and_correct_ci_high=high,
            vulnerable_among_functionally_correct=vulnerable_among_correct,
            vulnerability_rate_among_correct=(vulnerable_among_correct / functional if functional else math.nan),
        )
        output.append(record)
    return output


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_path", type=Path)
    parser.add_argument("--group-by", nargs="+", default=["condition", "agent"])
    args = parser.parse_args()
    rows = load_rows(args.csv_path)
    if not rows:
        raise SystemExit("input CSV has no data rows")
    unknown = [key for key in args.group_by if key not in rows[0]]
    if unknown:
        raise SystemExit(f"unknown grouping columns: {', '.join(unknown)}")
    summary = summarise(rows, args.group_by)
    writer = csv.DictWriter(sys.stdout, fieldnames=list(summary[0].keys()))
    writer.writeheader()
    writer.writerows(summary)
    return 0


if __name__ == "__main__":
    import sys

    raise SystemExit(main())

