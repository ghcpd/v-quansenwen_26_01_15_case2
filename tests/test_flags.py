import unittest

from src.flags import FeatureFlagStore


class TestFlags(unittest.TestCase):
    def test_flags_disabled_by_default(self):
        """Flags default to disabled when not in config."""
        store = FeatureFlagStore({})
        self.assertFalse(store.is_enabled("audit"))
        self.assertFalse(store.is_enabled("metrics"))

    def test_flags_can_be_enabled(self):
        """Flags can be explicitly enabled."""
        store = FeatureFlagStore({"audit": True, "metrics": True})
        self.assertTrue(store.is_enabled("audit"))
        self.assertTrue(store.is_enabled("metrics"))

    def test_unknown_flags_are_disabled(self):
        """Unknown flags are always disabled."""
        store = FeatureFlagStore({"unknown": True})
        self.assertFalse(store.is_enabled("unknown"))


if __name__ == "__main__":
    unittest.main()

