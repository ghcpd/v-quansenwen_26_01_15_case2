import json
from pathlib import Path

from src.api import run_workflow


def test_retries_and_continue(tmp_path: Path):
    config = {
        "name": "t",
        "retries": 3,
        "steps": [
            {"name": "bad", "action": "missing", "input": "x"},
            {"name": "good", "action": "echo", "input": "y"},
        ],
    }
    path = tmp_path / "cfg.json"
    path.write_text(json.dumps(config), encoding="utf-8")

    result = run_workflow(str(path))
    # After retries, workflow should continue to the next step
    assert result["results"][-1]["name"] == "good"
