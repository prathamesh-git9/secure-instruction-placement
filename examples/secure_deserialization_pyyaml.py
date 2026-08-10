"""Known-safe fixture for an infrastructure-only verifier pilot."""

import yaml


def restore_workspace_from_yaml(state_yaml: str) -> dict:
    """Restore a mapping from untrusted YAML without constructing Python objects."""
    try:
        value = yaml.safe_load(state_yaml)
    except yaml.YAMLError:
        return {}
    return value if isinstance(value, dict) else {}
