import unittest

from src.flags import FeatureFlagStore, KNOWN_FLAGS


class FeatureFlagStoreTests(unittest.TestCase):
    def test_known_flags_default_false(self):
        store = FeatureFlagStore({})
        for flag in KNOWN_FLAGS:
            self.assertFalse(store.is_enabled(flag))

    def test_unknown_flags_always_false(self):
        store = FeatureFlagStore({"custom": True})
        self.assertFalse(store.is_enabled("custom"))

    def test_flag_enabled_if_set_true(self):
        store = FeatureFlagStore({"audit": True})
        self.assertTrue(store.is_enabled("audit"))

    def test_flag_disabled_if_set_false(self):
        store = FeatureFlagStore({"audit": False})
        self.assertFalse(store.is_enabled("audit"))


if __name__ == "__main__":
    unittest.main()

