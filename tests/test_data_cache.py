import time
import unittest

from projects.itinerary_planner.data_cache import DataCache, get_shared_cache


class TestDataCache(unittest.TestCase):
    def setUp(self) -> None:
        self.cache = DataCache(default_ttl_seconds=60.0)

    def test_set_and_get(self) -> None:
        self.cache.set("key1", {"value": 42})
        result = self.cache.get("key1")
        self.assertEqual(result, {"value": 42})

    def test_get_missing_returns_none(self) -> None:
        self.assertIsNone(self.cache.get("nonexistent"))

    def test_get_expired_returns_none(self) -> None:
        self.cache.set("expires_soon", "data", ttl=0.01)
        time.sleep(0.05)
        self.assertIsNone(self.cache.get("expires_soon"))

    def test_invalidate_removes_entry(self) -> None:
        self.cache.set("to_remove", "value")
        self.cache.invalidate("to_remove")
        self.assertIsNone(self.cache.get("to_remove"))

    def test_invalidate_nonexistent_is_safe(self) -> None:
        self.cache.invalidate("ghost")  # Should not raise

    def test_clear_empties_cache(self) -> None:
        self.cache.set("a", 1)
        self.cache.set("b", 2)
        self.cache.clear()
        self.assertEqual(len(self.cache), 0)

    def test_len_counts_entries(self) -> None:
        self.cache.set("x", 1)
        self.cache.set("y", 2)
        self.assertEqual(len(self.cache), 2)

    def test_purge_expired(self) -> None:
        self.cache.set("fresh", "still here", ttl=60)
        self.cache.set("stale", "gone", ttl=0.01)
        time.sleep(0.05)
        removed = self.cache.purge_expired()
        self.assertEqual(removed, 1)
        self.assertIsNone(self.cache.get("stale"))
        self.assertEqual(self.cache.get("fresh"), "still here")

    def test_get_shared_cache_singleton(self) -> None:
        c1 = get_shared_cache()
        c2 = get_shared_cache()
        self.assertIs(c1, c2)

    def test_custom_ttl_overrides_default(self) -> None:
        short_cache = DataCache(default_ttl_seconds=100)
        short_cache.set("key", "val", ttl=0.01)
        time.sleep(0.05)
        self.assertIsNone(short_cache.get("key"))


if __name__ == "__main__":
    unittest.main()
