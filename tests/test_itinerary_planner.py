import unittest

from projects.itinerary_planner.data import DEFAULT_ATTRACTIONS, DEFAULT_SHOWS
from projects.itinerary_planner.planner import build_itinerary


class TestItineraryPlanner(unittest.TestCase):
    def test_build_itinerary_returns_timeline(self) -> None:
        timeline = build_itinerary(
            preferences={"family": 0.7, "thrill": 0.6, "photo": 0.5},
            start_time="09:00",
            available_hours=8,
            attractions=DEFAULT_ATTRACTIONS,
            shows=DEFAULT_SHOWS,
        )
        self.assertGreater(len(timeline), 0)
        self.assertTrue(all(x.start < x.end for x in timeline))
        self.assertTrue(all(timeline[i].start <= timeline[i + 1].start for i in range(len(timeline) - 1)))

    def test_zero_preferences_still_works(self) -> None:
        timeline = build_itinerary(
            preferences={"family": 0, "thrill": 0, "photo": 0},
            start_time="10:00",
            available_hours=2,
            attractions=DEFAULT_ATTRACTIONS,
            shows=DEFAULT_SHOWS,
        )
        self.assertIsInstance(timeline, list)
        self.assertTrue(all(x.start < x.end for x in timeline))


if __name__ == "__main__":
    unittest.main()
