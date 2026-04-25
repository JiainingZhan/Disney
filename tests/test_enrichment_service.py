"""Tests for EnrichmentService."""

import unittest
from unittest.mock import MagicMock, patch

from projects.itinerary_planner.data import Attraction, Show
from projects.itinerary_planner.data_cache import DataCache
from projects.itinerary_planner.enrichment_service import EnrichmentService, _crowd_factor_from_wait, _parse_time
from projects.itinerary_planner.themepark_client import ThemeParkClient


def _make_service() -> EnrichmentService:
    """Return an EnrichmentService backed by a fresh cache and offline client."""
    cache = DataCache(default_ttl_seconds=60)
    client = ThemeParkClient(cache=cache)
    client._http_get = MagicMock(return_value=None)  # type: ignore[method-assign]
    return EnrichmentService(client=client, cache=cache)


class TestEnrichmentService(unittest.TestCase):
    def test_get_attractions_returns_typed_objects(self) -> None:
        svc = _make_service()
        attractions = svc.get_attractions("magic-kingdom")
        self.assertGreater(len(attractions), 0)
        for a in attractions:
            self.assertIsInstance(a, Attraction)

    def test_get_shows_returns_typed_objects(self) -> None:
        svc = _make_service()
        shows = svc.get_shows("magic-kingdom")
        self.assertGreater(len(shows), 0)
        for s in shows:
            self.assertIsInstance(s, Show)

    def test_shows_have_valid_start_times(self) -> None:
        svc = _make_service()
        shows = svc.get_shows("magic-kingdom")
        from datetime import time
        for s in shows:
            self.assertIsInstance(s.start_time, time)

    def test_attractions_cached_on_second_call(self) -> None:
        svc = _make_service()
        first = svc.get_attractions("epcot")
        second = svc.get_attractions("epcot")
        self.assertEqual([a.name for a in first], [a.name for a in second])

    def test_unknown_park_returns_empty_lists(self) -> None:
        svc = _make_service()
        attractions = svc.get_attractions("narnia-park")
        shows = svc.get_shows("narnia-park")
        self.assertEqual(attractions, [])
        self.assertEqual(shows, [])

    def test_all_parks_return_lists(self) -> None:
        svc = _make_service()
        from projects.itinerary_planner.park_config import PARKS
        for slug in PARKS:
            attractions = svc.get_attractions(slug)
            shows = svc.get_shows(slug)
            self.assertIsInstance(attractions, list)
            self.assertIsInstance(shows, list)


class TestEnrichmentHelpers(unittest.TestCase):
    def test_crowd_factor_low_wait(self) -> None:
        self.assertAlmostEqual(_crowd_factor_from_wait(10), 0.8)

    def test_crowd_factor_moderate_wait(self) -> None:
        self.assertAlmostEqual(_crowd_factor_from_wait(25), 1.0)

    def test_crowd_factor_high_wait(self) -> None:
        self.assertAlmostEqual(_crowd_factor_from_wait(45), 1.2)

    def test_crowd_factor_very_high_wait(self) -> None:
        self.assertAlmostEqual(_crowd_factor_from_wait(90), 1.5)

    def test_parse_time_valid(self) -> None:
        from datetime import time
        result = _parse_time("21:00")
        self.assertEqual(result, time(hour=21, minute=0))

    def test_parse_time_invalid_returns_none(self) -> None:
        self.assertIsNone(_parse_time("not-a-time"))
        self.assertIsNone(_parse_time(""))


if __name__ == "__main__":
    unittest.main()
