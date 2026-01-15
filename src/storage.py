import json
import time
from pathlib import Path


class JsonFileStorage:
    """Append-only JSON storage for audit records."""

    def __init__(self, path: str) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def write_event(self, event: dict) -> None:
        payload = dict(event)
        payload.setdefault("ts", int(time.time()))
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload) + "\n")
