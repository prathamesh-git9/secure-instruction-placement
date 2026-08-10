#!/usr/bin/env python3
"""Audit development-task security oracles with deterministic unsafe mutants."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def canonical_hash(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def development_task_ids(split: dict) -> set[str]:
    return {item["task_id"] for item in split["development_tasks"]}


def validate_mutation_scope(config: dict, split: dict) -> None:
    development = development_task_ids(split)
    holdout = set(split["confirmatory_holdout_tasks"])
    seen: set[str] = set()
    for mutation in config["mutations"]:
        mutation_id = mutation["mutation_id"]
        task_id = mutation["task_id"]
        if mutation_id in seen:
            raise ValueError(f"duplicate mutation_id: {mutation_id}")
        seen.add(mutation_id)
        if task_id not in development:
            raise ValueError(f"mutation task is not development-only: {task_id}")
        if task_id in holdout:
            raise ValueError(f"mutation task overlaps protected holdout: {task_id}")
        if not mutation["verifier_path"].startswith("/verify/"):
            raise ValueError(f"invalid verifier path for {mutation_id}")
        if not mutation.get("replacements"):
            raise ValueError(f"no replacements for {mutation_id}")


def apply_mutation(source: str, replacements: list[dict[str, str]], mutation_id: str) -> str:
    mutant = source
    for index, replacement in enumerate(replacements, start=1):
        before = replacement["before"]
        after = replacement["after"]
        count = mutant.count(before)
        if count != 1:
            raise ValueError(
                f"{mutation_id} replacement {index}: expected one exact anchor, found {count}"
            )
        mutant = mutant.replace(before, after, 1)
    if mutant == source:
        raise ValueError(f"{mutation_id}: mutation made no change")
    return mutant


def post_code(endpoint: str, code: str, timeout: int) -> dict:
    payload = json.dumps(
        {
            "token": "local-eval-token",
            "code": code,
            "prompt": "development-only security-oracle mutation audit",
            "prompt_path": "committed-deterministic-mutant",
            "model_name": "oracle-mutation-audit",
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
    functional_failed = int(functional["total_failures"]) + int(functional["total_errors"])
    security_failed = int(security["total_failures"]) + int(security["total_errors"])
    functional_total = int(functional["total_tests"])
    security_total = int(security["total_tests"])
    return {
        "functional_total": functional_total,
        "functional_failed": functional_failed,
        "security_total": security_total,
        "security_failed": security_failed,
        "functional_preserved": functional_total > 0 and functional_failed == 0,
        "security_detected": security_total > 0 and security_failed > 0,
        "killed": functional_total > 0 and functional_failed == 0 and security_total > 0 and security_failed > 0,
    }


def prepare_mutants(repo: Path, config: dict) -> list[tuple[dict, str, str]]:
    prepared = []
    for mutation in config["mutations"]:
        source_path = (repo / mutation["source"]).resolve()
        if repo.resolve() not in source_path.parents:
            raise ValueError(f"source escapes repository: {mutation['source']}")
        source = source_path.read_text(encoding="utf-8")
        mutant = apply_mutation(source, mutation["replacements"], mutation["mutation_id"])
        prepared.append((mutation, source, mutant))
    return prepared


def run_audit(repo: Path, config: dict, endpoint: str, timeout: int) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for mutation, source, mutant in prepare_mutants(repo, config):
        result = post_code(endpoint.rstrip("/") + mutation["verifier_path"], mutant, timeout)
        rows.append(
            {
                "mutation_id": mutation["mutation_id"],
                "task_id": mutation["task_id"],
                "description": mutation["description"],
                "source": mutation["source"],
                "source_sha256": sha256_text(source),
                "mutant_sha256": sha256_text(mutant),
                **parse_counts(result),
            }
        )
    return rows


def build_manifest(config: dict, rows: list[dict[str, object]]) -> dict:
    killed = sum(bool(row["killed"]) for row in rows)
    return {
        "schema_version": "0.1.0",
        "audit": "development-security-oracle-mutation-audit",
        "scope": "development-only; protected holdout not read or executed",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "config_sha256": canonical_hash(config),
        "mutants_total": len(rows),
        "mutants_killed": killed,
        "mutation_score": killed / len(rows) if rows else 0.0,
        "rows": rows,
    }


def write_outputs(output: Path, manifest: dict) -> None:
    output.mkdir(parents=True, exist_ok=True)
    (output / "audit.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n")
    fields = [
        "mutation_id", "task_id", "description", "source", "source_sha256", "mutant_sha256",
        "functional_total", "functional_failed", "security_total", "security_failed",
        "functional_preserved", "security_detected", "killed",
    ]
    with (output / "audit.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(manifest["rows"])


def validate_existing(repo: Path, config: dict, output: Path) -> None:
    manifest = load_json(output / "audit.json")
    if manifest["config_sha256"] != canonical_hash(config):
        raise ValueError("committed audit config hash does not match")
    prepared = {m["mutation_id"]: (m, s, u) for m, s, u in prepare_mutants(repo, config)}
    if len(manifest["rows"]) != len(prepared):
        raise ValueError("committed audit row count does not match config")
    for row in manifest["rows"]:
        mutation_id = row["mutation_id"]
        if mutation_id not in prepared:
            raise ValueError(f"unknown committed mutation: {mutation_id}")
        mutation, source, mutant = prepared[mutation_id]
        expected = {
            "task_id": mutation["task_id"],
            "source": mutation["source"],
            "source_sha256": sha256_text(source),
            "mutant_sha256": sha256_text(mutant),
        }
        for key, value in expected.items():
            if row.get(key) != value:
                raise ValueError(f"{mutation_id}: committed {key} does not match")
        expected_functional = int(row["functional_total"]) > 0 and int(row["functional_failed"]) == 0
        expected_security = int(row["security_total"]) > 0 and int(row["security_failed"]) > 0
        expected_killed = expected_functional and expected_security
        if row.get("functional_preserved") is not expected_functional:
            raise ValueError(f"{mutation_id}: functional flag is inconsistent with counts")
        if row.get("security_detected") is not expected_security:
            raise ValueError(f"{mutation_id}: security flag is inconsistent with counts")
        if row.get("killed") is not expected_killed or not expected_killed:
            raise ValueError(f"{mutation_id}: committed evidence does not show a killed mutant")
    killed = sum(bool(row["killed"]) for row in manifest["rows"])
    if manifest["mutants_total"] != len(prepared) or manifest["mutants_killed"] != killed:
        raise ValueError("committed audit summary is inconsistent")
    expected_score = killed / len(prepared) if prepared else 0.0
    if manifest["mutation_score"] != expected_score:
        raise ValueError("committed mutation score is inconsistent")

    with (output / "audit.csv").open(encoding="utf-8", newline="") as handle:
        csv_rows = list(csv.DictReader(handle))
    if len(csv_rows) != len(manifest["rows"]):
        raise ValueError("committed CSV row count does not match JSON")
    for json_row, csv_row in zip(manifest["rows"], csv_rows):
        for key, value in json_row.items():
            if csv_row.get(key) != str(value):
                raise ValueError(f"{json_row['mutation_id']}: CSV {key} does not match JSON")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=Path("configs/development_oracle_mutations.json"))
    parser.add_argument("--output", type=Path, default=Path("results/development_oracle_mutation_audit_2026-08-10"))
    parser.add_argument("--endpoint", default="http://localhost:24684")
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--validate-existing", action="store_true")
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[1]
    config_path = (repo / args.config).resolve() if not args.config.is_absolute() else args.config.resolve()
    output = (repo / args.output).resolve() if not args.output.is_absolute() else args.output.resolve()
    config = load_json(config_path)
    split_path = (repo / config["split_config"]).resolve()
    split = load_json(split_path)
    validate_mutation_scope(config, split)
    try:
        if args.validate_existing:
            validate_existing(repo, config, output)
            print(f"validated {output}")
        else:
            rows = run_audit(repo, config, args.endpoint, args.timeout)
            manifest = build_manifest(config, rows)
            write_outputs(output, manifest)
            print(json.dumps({key: manifest[key] for key in ("mutants_total", "mutants_killed", "mutation_score")}))
            if manifest["mutants_killed"] != manifest["mutants_total"]:
                return 1
    except (OSError, ValueError, KeyError, TypeError, HTTPError, URLError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
