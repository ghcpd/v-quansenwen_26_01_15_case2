from src.flags import FeatureFlagStore


def test_flags_enabled_by_default():
    store = FeatureFlagStore({})
    assert store.is_enabled("audit") is True
