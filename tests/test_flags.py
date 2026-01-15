import unittest

from src.flags import FeatureFlagStore


class FeatureFlagStoreTests(unittest.TestCase):
    def test_flags_default_disabled(self) -> None:
        store = FeatureFlagStore({})
        self.assertFalse(store.is_enabled("audit"))
        self.assertFalse(store.is_enabled("metrics"))

    def test_known_flag_enabled_when_true(self) -> None:
        store = FeatureFlagStore({"audit": True})
        self.assertTrue(store.is_enabled("audit"))

    def test_unknown_flag_is_disabled(self) -> None:
        store = FeatureFlagStore({"custom": True})
        self.assertFalse(store.is_enabled("custom"))


if __name__ == "__main__":
    unittest.main()
