#!/usr/bin/env python3
"""Validate provenance and executable-test fields for task manifests.

This intentionally uses only the Python standard library. JSON Schema files are
the publication contract; this lightweight validator catches the highest-risk
dataset mistakes without requiring an environment dependency.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse


CWE_RE = re.compile(r"^CWE-[0-9]+$")
TASK_ID_RE = re.compile(r"^[a-z0-9][a-z0-9_-]+$")
REQUIRED_TOP = {"task_id", "title", "language", "cwe", "source", "license", "commands"}


def is_https_url(value: object) -> bool:
    if not isinstance(value, str):
        return False
    parsed = urlparse(value)
    return parsed.scheme == "https" and bool(parsed.netloc)


def validate_manifest(data: object, path: Path) -> list[str]:
    errors: list[str] = []
    prefix = str(path)
    if not isinstance(data, dict):
        return [f"{prefix}: manifest must be a JSON object"]

    missing = sorted(REQUIRED_TOP - data.keys())
    if missing:
        errors.append(f"{prefix}: missing fields: {', '.join(missing)}")

    task_id = data.get("task_id")
    if not isinstance(task_id, str) or not TASK_ID_RE.fullmatch(task_id):
        errors.append(f"{prefix}: invalid task_id")

    cwes = data.get("cwe")
    if not isinstance(cwes, list) or not cwes or any(not isinstance(cwe, str) or not CWE_RE.fullmatch(cwe) for cwe in cwes):
        errors.append(f"{prefix}: cwe must be a non-empty list like ['CWE-79']")
    elif len(cwes) != len(set(cwes)):
        errors.append(f"{prefix}: cwe entries must be unique")

    source = data.get("source")
    for key in ("name", "url", "revision", "retrieved_at"):
        if not isinstance(source, dict) or not source.get(key):
            errors.append(f"{prefix}: source.{key} is required")
    if isinstance(source, dict) and not is_https_url(source.get("url")):
        errors.append(f"{prefix}: source.url must be HTTPS")

    license_info = data.get("license")
    if not isinstance(license_info, dict):
        errors.append(f"{prefix}: license must be an object")
    else:
        if not license_info.get("spdx"):
            errors.append(f"{prefix}: license.spdx is required")
        if not is_https_url(license_info.get("evidence_url")):
            errors.append(f"{prefix}: license.evidence_url must be HTTPS")
        if license_info.get("adaptation_allowed") is not True:
            errors.append(f"{prefix}: task cannot enter the adapted benchmark without documented adaptation permission")

    commands = data.get("commands")
    if not isinstance(commands, dict):
        errors.append(f"{prefix}: commands must be an object")
    else:
        for key in ("functional_test", "security_test"):
            value = commands.get(key)
            if not isinstance(value, list) or not value or any(not isinstance(command, str) or not command.strip() for command in value):
                errors.append(f"{prefix}: commands.{key} must be a non-empty string list")

    return errors


def validate_tree(root: Path) -> tuple[int, list[str]]:
    manifests = sorted(root.rglob("manifest.json"))
    if not manifests:
        return 0, [f"{root}: no manifest.json files found"]

    errors: list[str] = []
    seen_ids: dict[str, Path] = {}
    for path in manifests:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{path}: cannot read valid JSON: {exc}")
            continue
        errors.extend(validate_manifest(data, path))
        if isinstance(data, dict) and isinstance(data.get("task_id"), str):
            task_id = data["task_id"]
            if task_id in seen_ids:
                errors.append(f"{path}: duplicate task_id '{task_id}' also used by {seen_ids[task_id]}")
            else:
                seen_ids[task_id] = path
    return len(manifests), errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path, help="Directory containing task subdirectories")
    args = parser.parse_args()
    count, errors = validate_tree(args.root)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print(f"Validated {count} task manifest(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

