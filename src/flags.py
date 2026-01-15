from dataclasses import dataclass

KNOWN_FLAGS = {"audit", "metrics", "parallel"}


@dataclass
class FeatureFlagStore:
    flags: dict

    def is_enabled(self, name: str) -> bool:
        if name not in KNOWN_FLAGS:
            return False
        return bool(self.flags.get(name, False))
