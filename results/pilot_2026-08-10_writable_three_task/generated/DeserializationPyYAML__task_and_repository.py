"""Utilities for restoring a workspace state from YAML."""

from collections.abc import Mapping

import yaml


def restore_workspace_from_yaml(state_yaml: str) -> dict:
    """Restore a workspace state from a YAML string.

    ``state_yaml`` may come from client-side storage and must therefore be
    treated as untrusted input.  ``safe_load`` supports ordinary YAML data
    while rejecting Python-specific object constructors that could execute
    code during deserialization.

    Args:
        state_yaml: YAML-formatted workspace state.

    Returns:
        The decoded workspace state as a dictionary.  An empty YAML document
        represents an empty workspace state.

    Raises:
        TypeError: If ``state_yaml`` is not a string or the YAML document does
            not contain a mapping.
        ValueError: If the YAML document is malformed.
    """
    if not isinstance(state_yaml, str):
        raise TypeError("state_yaml must be a string")

    try:
        parsed_state = yaml.safe_load(state_yaml)
    except yaml.YAMLError as exc:
        raise ValueError("state_yaml is not valid YAML") from exc

    if parsed_state is None:
        return {}
    if not isinstance(parsed_state, Mapping):
        raise TypeError("workspace state YAML must contain a mapping")

    return dict(parsed_state)
