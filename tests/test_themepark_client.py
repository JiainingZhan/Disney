"""Tests for ThemeParkClient — exercises fallback/mock paths."""

import json
import unittest
from unittest.mock import MagicMock, patch

from projects.itinerary_planner.data_cache import DataCache
from projects.itinerary_planner.themepark_client import ThemeParkClient


class TestThemeParkClientMockFallback(unittest.TestCase):
    """Verify that mock data is returned when the API is unreachable."""

    def setUp(self) -> None:
        # Fresh cache per test
        self.cache = DataCache(default_ttl_seconds=60)
        self.client = ThemeParkClient(cache=self.cache)

    def _make_client_offline(self, client: ThemeParkClient) -> None:
        """Patch _http_get to always return None (simulates network failure)."""
        client._http_get = MagicMock(return_value=None)  # type: ignore[method-assign]

    def test_get_attractions_magic_kingdom_fallback(self) -> None:
        self._make_client_offline(self.client)
        attractions = self.client.get_attractions("magic-kingdom")
        self.assertGreater(len(attractions), 0)
        names = [a["name"] for a in attractions]
        self.assertIn("Space Mountain", names)

    def test_get_attractions_tokyo_disneysea_fallback(self) -> None:
        self._make_client_offline(self.client)
        attractions = self.client.get_attractions("tokyo-disneysea")
        self.assertGreater(len(attractions), 0)
        names = [a["name"] for a in attractions]
        self.assertIn("Journey to the Center of the Earth", names)

    def test_get_shows_magic_kingdom_fallback(self) -> None:
        self._make_client_offline(self.client)
        shows = self.client.get_shows("magic-kingdom")
        self.assertGreater(len(shows), 0)
        names = [s["name"] for s in shows]
        self.assertIn("Happily Ever After", names)

    def test_unknown_park_returns_empty(self) -> None:
        self._make_client_offline(self.client)
        attractions = self.client.get_attractions("narnia-theme-park")
        self.assertEqual(attractions, [])

    def test_results_are_cached(self) -> None:
        self._make_client_offline(self.client)
        first = self.client.get_attractions("epcot")
        second = self.client.get_attractions("epcot")
        self.assertEqual(first, second)

    def test_get_live_wait_times_offline_returns_empty(self) -> None:
        self._make_client_offline(self.client)
        wait_times = self.client.get_live_wait_times("magic-kingdom")
        self.assertIsInstance(wait_times, dict)

    def test_get_live_wait_times_parses_api_response(self) -> None:
        mock_response = {
            "liveData": [
                {"id": "mk-space-mountain", "queue": {"STANDBY": {"waitTime": 55}}},
                {"id": "mk-pirates", "queue": {"STANDBY": {"waitTime": None}}},
            ]
        }
        self.client._http_get = MagicMock(return_value=mock_response)  # type: ignore[method-assign]
        result = self.client.get_live_wait_times("magic-kingdom")
        self.assertEqual(result.get("mk-space-mountain"), 55)
        self.assertNotIn("mk-pirates", result)  # waitTime=None should be excluded

    def test_all_parks_have_mock_attractions_or_empty(self) -> None:
        self._make_client_offline(self.client)
        from projects.itinerary_planner.park_config import PARKS
        for slug in PARKS:
            result = self.client.get_attractions(slug)
            self.assertIsInstance(result, list)

    def test_attraction_has_required_fields(self) -> None:
        self._make_client_offline(self.client)
        attractions = self.client.get_attractions("magic-kingdom")
        required = {"id", "name", "type", "wait_min", "tags"}
        for a in attractions:
            missing = required - a.keys()
            self.assertFalse(missing, f"Attraction '{a.get('name')}' missing fields: {missing}")


if __name__ == "__main__":
    unittest.main()
