import unittest
from datetime import time

from projects.itinerary_planner.data import DEFAULT_ATTRACTIONS, DEFAULT_SHOWS, Attraction, Show
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

    def test_meal_break_inserted(self) -> None:
        timeline = build_itinerary(
            preferences={"family": 0.6, "thrill": 0.6, "photo": 0.4},
            start_time="09:00",
            available_hours=8,
            attractions=DEFAULT_ATTRACTIONS,
            shows=DEFAULT_SHOWS,
            include_meal_break=True,
        )
        meal_items = [item for item in timeline if item.item_type == "meal"]
        self.assertGreater(len(meal_items), 0)

    def test_fastpass_priority_flag_accepted(self) -> None:
        """Ensure fastpass_priority flag does not raise and produces a timeline."""
        timeline = build_itinerary(
            preferences={"family": 0.6, "thrill": 0.8, "photo": 0.4},
            start_time="09:00",
            available_hours=8,
            attractions=DEFAULT_ATTRACTIONS,
            shows=DEFAULT_SHOWS,
            fastpass_priority=True,
        )
        self.assertIsInstance(timeline, list)

    def test_no_duplicate_attractions(self) -> None:
        timeline = build_itinerary(
            preferences={"family": 0.7, "thrill": 0.7, "photo": 0.5},
            start_time="09:00",
            available_hours=8,
            attractions=DEFAULT_ATTRACTIONS,
            shows=DEFAULT_SHOWS,
        )
        attraction_names = [item.name for item in timeline if item.item_type == "attraction"]
        self.assertEqual(len(attraction_names), len(set(attraction_names)))

    def test_enhanced_attraction_fields(self) -> None:
        """Verify that Attraction supports new optional fields."""
        a = Attraction(
            name="Test Ride",
            duration_min=5,
            wait_min=20,
            crowd_factor=1.0,
            tags={"thrill": 0.8},
            land="Tomorrowland",
            attraction_type="ride",
            height_restriction="44 inches",
            fastpass=True,
            description="A test ride.",
        )
        self.assertEqual(a.land, "Tomorrowland")
        self.assertTrue(a.fastpass)
        self.assertEqual(a.height_restriction, "44 inches")

    def test_enhanced_show_fields(self) -> None:
        """Verify that Show supports new optional fields."""
        s = Show(
            name="Test Show",
            start_time=time(hour=15, minute=0),
            duration_min=20,
            tags={"family": 1.0},
            show_type="musical",
            description="A test show.",
        )
        self.assertEqual(s.show_type, "musical")
        self.assertEqual(s.description, "A test show.")

    def test_plan_item_has_land_and_notes(self) -> None:
        """PlanItem now carries land and notes fields."""
        from projects.itinerary_planner.planner import PlanItem
        from datetime import datetime
        item = PlanItem(
            name="Ride",
            item_type="attraction",
            start=datetime(2024, 1, 1, 9, 0),
            end=datetime(2024, 1, 1, 10, 0),
            score=0.5,
            land="Fantasyland",
            notes="Lightning Lane available",
        )
        self.assertEqual(item.land, "Fantasyland")
        self.assertIn("Lightning Lane", item.notes)


if __name__ == "__main__":
    unittest.main()
