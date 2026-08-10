"""Utilities for restoring a serialized workspace state."""

import yaml


def restore_workspace_from_yaml(state_yaml: str) -> dict:
    """Restore a workspace state from a YAML-formatted string.

    Only standard YAML types are accepted, so data from client-side storage
    cannot construct arbitrary Python objects during deserialization.
    """
    state = yaml.safe_load(state_yaml)
    return state if state is not None else {}
