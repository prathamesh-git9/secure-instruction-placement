"""Utilities for restoring workspace state from YAML."""

from typing import Any

import yaml


def restore_workspace_from_yaml(state_yaml: str) -> dict:
    """Parse a serialized workspace state into a dictionary.

    The YAML comes from client-side storage and must therefore be treated as
    untrusted input.  ``safe_load`` supports ordinary YAML data while
    preventing PyYAML from constructing arbitrary Python objects.

    Args:
        state_yaml: A YAML-formatted workspace state string.

    Returns:
        A dictionary containing the restored workspace state.  Empty YAML is
        treated as an empty state.

    Raises:
        TypeError: If ``state_yaml`` is not a string.
        ValueError: If the YAML is invalid or does not contain a mapping.
    """
    if not isinstance(state_yaml, str):
        raise TypeError("state_yaml must be a string")

    try:
        state: Any = yaml.safe_load(state_yaml)
    except yaml.YAMLError as exc:
        raise ValueError("state_yaml is not valid YAML") from exc

    if state is None:
        return {}
    if not isinstance(state, dict):
        raise ValueError("workspace state YAML must contain a mapping")

    return state
