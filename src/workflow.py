from dataclasses import dataclass
from typing import Callable, Dict, List

from .flags import FeatureFlagStore
from .storage import JsonFileStorage


@dataclass
class Step:
    name: str
    action: str
    input: str
    optional: bool = False
    priority: int = 0


class WorkflowEngine:
    def __init__(self, config: dict) -> None:
        self.config = config
        self.flags = FeatureFlagStore(config.get("flags", {}))
        storage_cfg = config.get("storage", {})
        self.storage = JsonFileStorage(storage_cfg.get("path", "./driftflow.audit.json"))
        self.max_attempts = int(config.get("max_attempts", 1))

    def run(self) -> List[dict]:
        steps = [self._build_step(item) for item in self.config.get("steps", [])]
        steps = sorted(steps, key=lambda s: (-s.priority, s.name))
        results: List[dict] = []
        for step in steps:
            result = self._run_step(step)
            results.append(result)
            if not result["ok"] and not step.optional:
                break
        return results

    def _build_step(self, data: dict) -> Step:
        return Step(
            name=data.get("name", "step"),
            action=data.get("action", "echo"),
            input=str(data.get("input", "")),
            optional=bool(data.get("optional", False)),
            priority=int(data.get("priority", 0)),
        )

    def _run_step(self, step: Step) -> dict:
        attempts = 1 if step.optional else self.max_attempts
        last_error = None
        for _ in range(attempts):
            try:
                output = self._dispatch(step.action)(step.input)
                result = {"name": step.name, "ok": True, "output": output}
                self._audit(step, result)
                return result
            except Exception as exc:  # noqa: BLE001
                last_error = exc
        result = {"name": step.name, "ok": False, "error": str(last_error)}
        self._audit(step, result)
        return result

    def _dispatch(self, action: str) -> Callable[[str], str]:
        handlers: Dict[str, Callable[[str], str]] = {
            "echo": lambda value: value,
            "upper": lambda value: value.upper(),
            "lower": lambda value: value.lower(),
            "reverse": lambda value: value[::-1],
        }
        if action not in handlers:
            raise ValueError(f"Unknown action: {action}")
        return handlers[action]

    def _audit(self, step: Step, result: dict) -> None:
        if not self.flags.is_enabled("audit"):
            return
        self.storage.write_event(
            {
                "step": step.name,
                "action": step.action,
                "ok": result.get("ok"),
            }
        )
