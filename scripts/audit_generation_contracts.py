#!/usr/bin/env python3
"""Audit prompt, verifier-signature, and params output targets."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

from run_source_pilot import load_task


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--upstream", type=Path, required=True)
    args = parser.parse_args()
    upstream = args.upstream.resolve()
    benchmark = json.loads(
        (upstream / "datasets" / "benchmark" / "python" / "python.json").read_text(encoding="utf-8")
    )
    rows: list[dict[str, object]] = []
    has_error = False
    for task_id in benchmark:
        try:
            task = load_task(upstream, task_id)
            rows.append(
                {
                    "task_id": task_id,
                    "status": "ok",
                    "prompt_signature_target": task["target"].as_posix(),
                    "params_targets": "|".join(task["metadata_targets"]),
                    "params_mismatch": task["metadata_target_mismatch"],
                    "error": "",
                }
            )
        except (OSError, KeyError, TypeError, ValueError) as exc:
            has_error = True
            rows.append(
                {
                    "task_id": task_id,
                    "status": "error",
                    "prompt_signature_target": "",
                    "params_targets": "",
                    "params_mismatch": "",
                    "error": str(exc),
                }
            )
    writer = csv.DictWriter(sys.stdout, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
    return 1 if has_error else 0


if __name__ == "__main__":
    raise SystemExit(main())
