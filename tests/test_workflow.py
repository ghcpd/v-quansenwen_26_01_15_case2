import json
import os
import tempfile
import unittest

from src.api import run_workflow


class TestWorkflow(unittest.TestCase):
    def test_non_optional_failure_stops_workflow(self):
        """A non-optional step failure should stop the workflow."""
        config = {
            "name": "test_stop",
            "max_attempts": 2,
            "steps": [
                {"name": "bad", "action": "missing", "input": "x"},
                {"name": "good", "action": "echo", "input": "y"},
            ],
        }
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            json.dump(config, f)
            path = f.name

        try:
            result = run_workflow(path)
            # Workflow should stop after first non-optional failure
            self.assertEqual(len(result["results"]), 1)
            self.assertEqual(result["results"][0]["name"], "bad")
            self.assertFalse(result["results"][0]["ok"])
            self.assertEqual(result["status"], "failed")
        finally:
            os.unlink(path)

    def test_optional_failure_continues_workflow(self):
        """An optional step failure should not stop the workflow."""
        config = {
            "name": "test_continue",
            "max_attempts": 2,
            "steps": [
                {"name": "bad", "action": "missing", "input": "x", "optional": True},
                {"name": "good", "action": "echo", "input": "y"},
            ],
        }
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            json.dump(config, f)
            path = f.name

        try:
            result = run_workflow(path)
            # Workflow should continue past optional failure
            self.assertEqual(len(result["results"]), 2)
            self.assertFalse(result["results"][0]["ok"])  # bad failed
            self.assertTrue(result["results"][1]["ok"])   # good succeeded
        finally:
            os.unlink(path)

    def test_steps_sorted_by_priority_then_name(self):
        """Steps should be sorted by priority (desc) then name (asc)."""
        config = {
            "name": "test_order",
            "steps": [
                {"name": "charlie", "action": "echo", "input": "c", "priority": 0},
                {"name": "alpha", "action": "echo", "input": "a", "priority": 0},
                {"name": "bravo", "action": "echo", "input": "b", "priority": 10},
            ],
        }
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            json.dump(config, f)
            path = f.name

        try:
            result = run_workflow(path)
            names = [r["name"] for r in result["results"]]
            # bravo has highest priority, then alpha and charlie sorted by name
            self.assertEqual(names, ["bravo", "alpha", "charlie"])
        finally:
            os.unlink(path)

    def test_actions_work_correctly(self):
        """Test that all actions produce expected output."""
        config = {
            "name": "test_actions",
            "steps": [
                {"name": "a", "action": "echo", "input": "hello", "priority": 4},
                {"name": "b", "action": "upper", "input": "hello", "priority": 3},
                {"name": "c", "action": "lower", "input": "HELLO", "priority": 2},
                {"name": "d", "action": "reverse", "input": "hello", "priority": 1},
            ],
        }
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            json.dump(config, f)
            path = f.name

        try:
            result = run_workflow(path)
            outputs = {r["name"]: r["output"] for r in result["results"]}
            self.assertEqual(outputs["a"], "hello")
            self.assertEqual(outputs["b"], "HELLO")
            self.assertEqual(outputs["c"], "hello")
            self.assertEqual(outputs["d"], "olleh")
        finally:
            os.unlink(path)

    def test_max_attempts_retries_on_failure(self):
        """Verify max_attempts controls retry behavior."""
        # With max_attempts=1, only one attempt is made
        config = {
            "name": "test_retries",
            "max_attempts": 1,
            "steps": [
                {"name": "fail", "action": "unknown", "input": "x"},
            ],
        }
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            json.dump(config, f)
            path = f.name

        try:
            result = run_workflow(path)
            self.assertEqual(result["status"], "failed")
            self.assertFalse(result["results"][0]["ok"])
        finally:
            os.unlink(path)


if __name__ == "__main__":
    unittest.main()
