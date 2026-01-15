import json
import tempfile
import unittest
from pathlib import Path

from src.api import run_workflow


class WorkflowEngineTests(unittest.TestCase):
    def _write_config(self, config: dict) -> Path:
        tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(tmpdir.cleanup)
        path = Path(tmpdir.name) / "config.json"
        path.write_text(json.dumps(config), encoding="utf-8")
        return path

    def test_non_optional_failure_stops_workflow(self) -> None:
        config = {
            "name": "t",
            "steps": [
                {"name": "bad", "action": "missing", "input": "x"},
                {"name": "good", "action": "echo", "input": "y"},
            ],
            "max_attempts": 1,
            "storage": {"path": "./ignored.json"},
        }
        result = run_workflow(str(self._write_config(config)))

        self.assertEqual(result["status"], "failed")
        self.assertEqual(len(result["results"]), 1)
        self.assertFalse(result["results"][0]["ok"])
        self.assertEqual(result["results"][0]["name"], "bad")

    def test_optional_failure_allows_following_steps(self) -> None:
        config = {
            "name": "t",
            "steps": [
                {"name": "maybe", "action": "missing", "input": "x", "optional": True},
                {"name": "good", "action": "echo", "input": "y"},
            ],
            "storage": {"path": "./ignored.json"},
        }
        result = run_workflow(str(self._write_config(config)))

        self.assertEqual(len(result["results"]), 2)
        self.assertFalse(result["results"][0]["ok"])
        self.assertTrue(result["results"][1]["ok"])
        self.assertEqual(result["results"][1]["output"], "y")
        self.assertEqual(result["status"], "failed")

    def test_priority_sorts_before_execution(self) -> None:
        config = {
            "name": "t",
            "steps": [
                {"name": "low", "action": "echo", "input": "a", "priority": 0},
                {"name": "high", "action": "reverse", "input": "abc", "priority": 1},
            ],
            "storage": {"path": "./ignored.json"},
        }
        result = run_workflow(str(self._write_config(config)))

        self.assertEqual([r["name"] for r in result["results"]], ["high", "low"])
        self.assertEqual(result["results"][0]["output"], "cba")


if __name__ == "__main__":
    unittest.main()
