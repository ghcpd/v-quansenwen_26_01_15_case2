import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from src.api import run_workflow


class TestWorkflow(unittest.TestCase):
    def test_retries_and_stop_on_failure(self):
        """Non-optional step failure stops workflow after max_attempts."""
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config = {
                "name": "t",
                "max_attempts": 3,
                "steps": [
                    {"name": "bad", "action": "missing", "input": "x"},
                    {"name": "good", "action": "echo", "input": "y"},
                ],
            }
            path = tmp_path / "cfg.json"
            path.write_text(json.dumps(config), encoding="utf-8")

            result = run_workflow(str(path))
            # After max_attempts, workflow should STOP (not continue to next step)
            self.assertEqual(len(result["results"]), 1)
            self.assertEqual(result["results"][0]["name"], "bad")
            self.assertFalse(result["results"][0]["ok"])
            self.assertEqual(result["status"], "failed")

    def test_optional_step_continues_on_failure(self):
        """Optional step failure does not stop workflow."""
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config = {
                "name": "t",
                "max_attempts": 3,
                "steps": [
                    {"name": "bad", "action": "missing", "input": "x", "optional": True},
                    {"name": "good", "action": "echo", "input": "y"},
                ],
            }
            path = tmp_path / "cfg.json"
            path.write_text(json.dumps(config), encoding="utf-8")

            result = run_workflow(str(path))
            # Workflow should continue to the next step
            self.assertEqual(len(result["results"]), 2)
            self.assertEqual(result["results"][0]["name"], "bad")
            self.assertFalse(result["results"][0]["ok"])
            self.assertEqual(result["results"][1]["name"], "good")
            self.assertTrue(result["results"][1]["ok"])

    def test_priority_ordering(self):
        """Steps execute by priority (highest first), then alphabetically."""
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config = {
                "name": "t",
                "steps": [
                    {"name": "zebra", "action": "echo", "input": "z", "priority": 0},
                    {"name": "apple", "action": "echo", "input": "a", "priority": 0},
                    {"name": "high", "action": "echo", "input": "h", "priority": 10},
                ],
            }
            path = tmp_path / "cfg.json"
            path.write_text(json.dumps(config), encoding="utf-8")

            result = run_workflow(str(path))
            names = [r["name"] for r in result["results"]]
            # Should be: high (priority 10), then apple, zebra (alphabetical)
            self.assertEqual(names, ["high", "apple", "zebra"])


if __name__ == "__main__":
    unittest.main()

