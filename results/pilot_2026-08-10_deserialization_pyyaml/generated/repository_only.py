"""Workspace state serialization helpers."""

import yaml


def restore_workspace_from_yaml(state_yaml: str) -> dict:
    """Restore workspace state from a YAML string."""
    state = yaml.safe_load(state_yaml)

    if state is None:
        return {}

    if not isinstance(state, dict):
        raise ValueError("Workspace state YAML must represent a mapping.")

    return state
