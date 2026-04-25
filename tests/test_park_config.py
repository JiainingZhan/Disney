import unittest

from projects.itinerary_planner.park_config import PARKS, get_park, list_parks


class TestParkConfig(unittest.TestCase):
    def test_parks_not_empty(self) -> None:
        self.assertGreater(len(PARKS), 0)

    def test_all_required_parks_present(self) -> None:
        required_slugs = [
            "magic-kingdom",
            "epcot",
            "hollywood-studios",
            "animal-kingdom",
            "disneyland",
            "tokyo-disneyland",
            "tokyo-disneysea",
            "disneyland-paris",
            "hong-kong-disneyland",
            "shanghai-disneyland",
        ]
        for slug in required_slugs:
            self.assertIn(slug, PARKS, f"Park slug '{slug}' not found in PARKS registry")

    def test_get_park_returns_config(self) -> None:
        park = get_park("magic-kingdom")
        self.assertIsNotNone(park)
        self.assertEqual(park.slug, "magic-kingdom")
        self.assertIn("USA", park.country)

    def test_get_park_unknown_returns_none(self) -> None:
        result = get_park("imaginary-park")
        self.assertIsNone(result)

    def test_get_park_case_insensitive(self) -> None:
        self.assertIsNotNone(get_park("Magic-Kingdom"))

    def test_list_parks_returns_all(self) -> None:
        parks = list_parks()
        self.assertEqual(len(parks), len(PARKS))

    def test_park_has_required_fields(self) -> None:
        for slug, park in PARKS.items():
            self.assertTrue(park.name, f"Park '{slug}' has empty name")
            self.assertTrue(park.timezone, f"Park '{slug}' has empty timezone")
            self.assertTrue(park.default_open, f"Park '{slug}' has empty default_open")
            self.assertTrue(park.default_close, f"Park '{slug}' has empty default_close")

    def test_lands_are_lists(self) -> None:
        for slug, park in PARKS.items():
            self.assertIsInstance(park.lands, list, f"Park '{slug}'.lands is not a list")


if __name__ == "__main__":
    unittest.main()
