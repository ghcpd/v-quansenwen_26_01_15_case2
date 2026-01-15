import json
import tempfile
import unittest
from pathlib import Path

from src.api import run_workflow
from src.workflow import WorkflowEngine


class WorkflowTests(unittest.TestCase):
    def _write_config(self, tmp_dir: Path, cfg: dict) -> Path:
        path = tmp_dir / "cfg.json"
        path.write_text(json.dumps(cfg), encoding="utf-8")
        return path

    def test_non_optional_failure_stops_workflow(self):
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            cfg = {
                "name": "t",
                "max_attempts": 2,
                "steps": [
                    {"name": "bad", "action": "missing", "input": "x"},
                    {"name": "good", "action": "echo", "input": "y"},
                ],
            }
            path = self._write_config(tmp, cfg)
            result = run_workflow(str(path))

            self.assertEqual(result["status"], "failed")
            self.assertEqual(len(result["results"]), 1)
            self.assertFalse(result["results"][0]["ok"])
            self.assertIn("Unknown action", result["results"][0].get("error", ""))

    def test_optional_failure_does_not_stop_but_marks_failed(self):
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            cfg = {
                "name": "t",
                "max_attempts": 3,
                "steps": [
                    {"name": "maybe", "action": "missing", "input": "x", "optional": True, "priority": 10},
                    {"name": "good", "action": "echo", "input": "y", "priority": 0},
                ],
            }
            path = self._write_config(tmp, cfg)
            result = run_workflow(str(path))

            self.assertEqual(len(result["results"]), 2)
            names = [r["name"] for r in result["results"]]
            self.assertEqual(names, ["maybe", "good"])
            self.assertFalse(result["results"][0]["ok"])
            self.assertTrue(result["results"][1]["ok"])
            # Optional failure still contributes to overall status today
            self.assertEqual(result["status"], "failed")

    def test_priority_sorting_and_name_tiebreak(self):
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            cfg = {
                "steps": [
                    {"name": "zeta", "action": "echo", "input": "1", "priority": 5},
                    {"name": "alpha", "action": "echo", "input": "2", "priority": 5},
                    {"name": "mid", "action": "echo", "input": "3", "priority": 0},
                ]
            }
            path = self._write_config(tmp, cfg)
            result = run_workflow(str(path))
            names = [r["name"] for r in result["results"]]
            outputs = [r.get("output") for r in result["results"]]

            self.assertEqual(names, ["alpha", "zeta", "mid"])
            self.assertEqual(outputs, ["2", "1", "3"])

    def test_audit_written_when_flag_enabled(self):
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            audit_path = tmp / "audit.jsonl"
            cfg = {
                "flags": {"audit": True},
                "storage": {"path": str(audit_path)},
                "steps": [
                    {"name": "one", "action": "echo", "input": "a"},
                    {"name": "two", "action": "upper", "input": "b"},
                ],
            }
            path = self._write_config(tmp, cfg)
            result = run_workflow(str(path))

            self.assertTrue(audit_path.exists())
            lines = audit_path.read_text(encoding="utf-8").strip().splitlines()
            self.assertEqual(len(lines), len(result["results"]))
            first_event = json.loads(lines[0])
            self.assertIn("step", first_event)
            self.assertIn("action", first_event)
            self.assertIn("ok", first_event)

    def test_no_audit_file_when_flag_disabled(self):
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            audit_path = tmp / "audit.jsonl"
            cfg = {
                "flags": {"audit": False},
                "storage": {"path": str(audit_path)},
                "steps": [{"name": "one", "action": "echo", "input": "a"}],
            }
            path = self._write_config(tmp, cfg)
            _ = run_workflow(str(path))

            self.assertFalse(audit_path.exists())

    def test_max_attempts_applied_only_to_non_optional(self):
        original_dispatch = WorkflowEngine._dispatch
        try:
            attempts = {"count": 0}

            def fake_dispatch(self, action):  # noqa: ANN001
                def inner(value):  # noqa: ANN001
                    attempts["count"] += 1
                    if attempts["count"] < self.max_attempts:
                        raise RuntimeError("boom")
                    return value

                return inner

            WorkflowEngine._dispatch = fake_dispatch

            with tempfile.TemporaryDirectory() as td:
                tmp = Path(td)
                cfg = {
                    "max_attempts": 3,
                    "steps": [{"name": "retry", "action": "anything", "input": "ok"}],
                }
                path = self._write_config(tmp, cfg)
                result = run_workflow(str(path))
                self.assertEqual(result["status"], "ok")
                self.assertEqual(attempts["count"], 3)

            # Optional step should only attempt once even if max_attempts is higher
            attempts["count"] = 0
            with tempfile.TemporaryDirectory() as td:
                tmp = Path(td)
                cfg = {
                    "max_attempts": 5,
                    "steps": [{"name": "opt", "action": "anything", "input": "ok", "optional": True}],
                }
                path = self._write_config(tmp, cfg)
                result = run_workflow(str(path))
                self.assertEqual(result["status"], "failed")
                self.assertEqual(attempts["count"], 1)
        finally:
            WorkflowEngine._dispatch = original_dispatch


if __name__ == "__main__":
    unittest.main()

