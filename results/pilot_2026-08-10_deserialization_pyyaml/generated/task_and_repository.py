"""Workspace state serialization and restoration utilities."""

from typing import Any

import yaml


def restore_workspace_from_yaml(state_yaml: str) -> dict:
    """Restore workspace state from a YAML string.

    Uses safe_load to prevent execution of arbitrary Python objects from
    untrusted client-side storage.
    """
    if not isinstance(state_yaml, str):
        raise TypeError("state_yaml must be a string")

    state: Any = yaml.safe_load(state_yaml)

    if state is None:
        return {}

    if not isinstance(state, dict):
        raise ValueError("workspace state YAML must represent a mapping")

    return state
