"""Utilities for restoring a user's workspace state."""

from typing import Any

import yaml


def restore_workspace_from_yaml(state_yaml: str) -> dict:
    """Parse a stored workspace-state YAML document.

    ``safe_load`` is used deliberately because the input originates from
    client-side storage and must not be allowed to construct arbitrary Python
    objects.

    Args:
        state_yaml: YAML-formatted workspace state.

    Returns:
        The workspace state as a dictionary. An empty YAML document produces
        an empty dictionary.

    Raises:
        TypeError: If ``state_yaml`` is not a string.
        ValueError: If the YAML document does not contain a mapping.
        yaml.YAMLError: If the YAML document is invalid.
    """
    if not isinstance(state_yaml, str):
        raise TypeError("state_yaml must be a string")

    state: Any = yaml.safe_load(state_yaml)
    if state is None:
        return {}
    if not isinstance(state, dict):
        raise ValueError("workspace state YAML must contain a mapping")
    return state
