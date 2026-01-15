import json
import os
from copy import deepcopy

DEFAULT_CONFIG = {
    "name": "workflow",
    "steps": [],
    "flags": {},
    "storage": {
        "type": "json",
        "path": "./driftflow.audit.json",
    },
    "max_attempts": 1,
    "timeout_seconds": 10,
}


def load_config(path: str) -> dict:
    """Load configuration from a JSON file and apply environment overrides."""
    with open(path, "r", encoding="utf-8") as handle:
        data = json.load(handle)

    config = deepcopy(DEFAULT_CONFIG)
    config.update(data or {})

    # Environment overrides (current behavior)
    timeout_env = os.getenv("WORKFLOW_TIMEOUT_SECONDS")
    if timeout_env:
        try:
            config["timeout_seconds"] = int(timeout_env)
        except ValueError:
            pass

    flags_env = os.getenv("DRIFTFLOW_FLAGS")
    if flags_env:
        disabled = {item.strip() for item in flags_env.split(",") if item.strip()}
        config.setdefault("flags", {})
        for flag in disabled:
            config["flags"][flag] = False

    return config
