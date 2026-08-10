"""Utilities for restoring serialized workspace state."""

from typing import Any

import yaml


def restore_workspace_from_yaml(state_yaml: str) -> dict:
    """Restore workspace state from a YAML string.

    Uses safe_load to prevent execution of arbitrary YAML constructors.
    """
    if not isinstance(state_yaml, str):
        raise TypeError("state_yaml must be a string")

    state: Any = yaml.safe_load(state_yaml)

    if state is None:
        return {}

    if not isinstance(state, dict):
        raise ValueError("workspace state YAML must contain a mapping")

    return state
