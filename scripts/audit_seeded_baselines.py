#!/usr/bin/env python3
"""Check whether SecCodeBench's Python oracles reject seeded vulnerable code."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


def target_source(repo_path: Path) -> Path:
    signature = json.loads((repo_path / "signature.json").read_text(encoding="utf-8"))
    module = signature.get("module_name")
    if not isinstance(module, str) or not module:
        raise ValueError(f"{repo_path}: missing Python module_name")
    return repo_path / "src" / module / f"{module}.py"


def local_endpoint(upstream_url: str, base_endpoint: str) -> str:
    path = urlparse(upstream_url).path
    return base_endpoint.rstrip("/") + path


def post_code(endpoint: str, code: str, timeout: int) -> dict:
    payload = json.dumps(
        {
            "token": "local-eval-token",
            "code": code,
            "prompt": "seeded vulnerable baseline oracle audit",
            "prompt_path": "upstream-baseline",
            "model_name": "upstream-vulnerable-baseline",
            "thinking": False,
        }
    ).encode("utf-8")
    request = Request(endpoint, data=payload, headers={"Content-Type": "application/json"}, method="POST")
    with urlopen(request, timeout=timeout) as response:
        return json.load(response)


def parse_counts(result: dict) -> dict[str, int | bool]:
    tests = result["test_result"]
    functional = tests["functional_result"]
    security = tests["security_result"]
    func_failed = int(functional["total_failures"]) + int(functional["total_errors"])
    sec_failed = int(security["total_failures"]) + int(security["total_errors"])
    return {
        "functional_total": int(functional["total_tests"]),
        "functional_failed": func_failed,
        "security_total": int(security["total_tests"]),
        "security_failed": sec_failed,
        "seed_detected": sec_failed > 0,
    }


def audit(upstream: Path, base_endpoint: str, timeout: int) -> list[dict[str, object]]:
    benchmark_path = upstream / "datasets" / "benchmark" / "python" / "python.json"
    benchmark = json.loads(benchmark_path.read_text(encoding="utf-8"))
    bench_root = upstream / "docker" / "model" / "python" / "python_bench"
    rows: list[dict[str, object]] = []
    for case_id, metadata in benchmark.items():
        upstream_url = metadata["verify_urls"]["gen"]
        parts = urlparse(upstream_url).path.strip("/").split("/")
        if len(parts) != 3 or parts[0] != "verify":
            rows.append({"case": case_id, "status": "invalid_verify_url", "error": upstream_url})
            continue
        repo_path = bench_root / parts[1] / parts[2]
        try:
            source_path = target_source(repo_path)
            code = source_path.read_text(encoding="utf-8")
            result = post_code(local_endpoint(upstream_url, base_endpoint), code, timeout)
            rows.append({"case": case_id, "status": "ok", **parse_counts(result), "source": str(source_path)})
        except (OSError, ValueError, KeyError, TypeError, HTTPError, URLError) as exc:
            rows.append({"case": case_id, "status": "error", "error": str(exc)})
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--upstream", type=Path, required=True)
    parser.add_argument("--endpoint", default="http://localhost:24684")
    parser.add_argument("--timeout", type=int, default=180)
    args = parser.parse_args()
    rows = audit(args.upstream.resolve(), args.endpoint, args.timeout)
    fields = sorted({key for row in rows for key in row})
    writer = csv.DictWriter(sys.stdout, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)
    return 1 if any(row["status"] != "ok" for row in rows) else 0


if __name__ == "__main__":
    raise SystemExit(main())

