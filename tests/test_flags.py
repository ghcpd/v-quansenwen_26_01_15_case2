import unittest

from src.flags import FeatureFlagStore, KNOWN_FLAGS


class TestFeatureFlagStore(unittest.TestCase):
    def test_flags_disabled_by_default(self):
        """Flags should be disabled when not explicitly set."""
        store = FeatureFlagStore({})
        self.assertFalse(store.is_enabled("audit"))
        self.assertFalse(store.is_enabled("metrics"))
        self.assertFalse(store.is_enabled("parallel"))

    def test_flags_enabled_when_set_true(self):
        """Flags should be enabled when explicitly set to True."""
        store = FeatureFlagStore({"audit": True, "metrics": True})
        self.assertTrue(store.is_enabled("audit"))
        self.assertTrue(store.is_enabled("metrics"))

    def test_unknown_flag_returns_false(self):
        """Unknown flags should always return False."""
        store = FeatureFlagStore({"unknown_flag": True})
        self.assertFalse(store.is_enabled("unknown_flag"))

    def test_known_flags_constant(self):
        """Verify the known flags set."""
        self.assertEqual(KNOWN_FLAGS, {"audit", "metrics", "parallel"})


if __name__ == "__main__":
    unittest.main()
