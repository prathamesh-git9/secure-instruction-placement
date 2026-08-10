import yaml


def restore_workspace_from_yaml(state_yaml: str) -> dict:
    """Restore workspace state from a YAML-formatted string."""
    return yaml.load(state_yaml, Loader=yaml.SafeLoader)
