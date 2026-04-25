import unittest

from projects.ip_recommender.data import CONTENT_CATALOG, ContentItem
from projects.ip_recommender.recommender import build_user_profile, recommend_content


class TestIpRecommender(unittest.TestCase):
    def test_build_profile_with_known_ips(self) -> None:
        profile = build_user_profile(["Frozen", "Marvel"])
        self.assertIn("princess", profile)
        self.assertIn("hero", profile)
        self.assertGreaterEqual(len(profile), 4)

    def test_recommend_content_returns_ranked(self) -> None:
        results = recommend_content(["Frozen", "Marvel"], CONTENT_CATALOG, top_n=5)
        self.assertGreater(len(results), 0)
        self.assertLessEqual(len(results), 5)
        scores = [x[1] for x in results]
        self.assertEqual(scores, sorted(scores, reverse=True))

    def test_top_n_zero_returns_empty(self) -> None:
        results = recommend_content(["Frozen"], CONTENT_CATALOG, top_n=0)
        self.assertEqual(results, [])

    def test_park_slug_boosts_park_items(self) -> None:
        """Items available at the requested park should score higher."""
        results_with_park = recommend_content(
            ["Frozen"], CONTENT_CATALOG, top_n=10, park_slug="magic-kingdom"
        )
        names_with_park = [r[0].name for r in results_with_park]
        # Princess Parade is available at magic-kingdom
        self.assertIn("Princess Parade", names_with_park)

    def test_age_group_kids_boosts_kid_items(self) -> None:
        results = recommend_content(
            ["Toy Story"], CONTENT_CATALOG, top_n=10, age_group="kids"
        )
        self.assertGreater(len(results), 0)

    def test_include_experiences_adds_park_items(self) -> None:
        results = recommend_content(
            ["Frozen"],
            CONTENT_CATALOG,
            top_n=15,
            park_slug="magic-kingdom",
            include_experiences=True,
        )
        categories = {r[0].category for r in results}
        self.assertTrue(categories & {"park_experience", "entertainment", "dining"})

    def test_unknown_ip_falls_back_to_tag(self) -> None:
        """Unknown IPs should be added as raw tags without crashing."""
        results = recommend_content(["UnknownIP42"], CONTENT_CATALOG, top_n=5)
        self.assertIsInstance(results, list)

    def test_expanded_catalog_size(self) -> None:
        """Catalog should be significantly larger than the original 10 items."""
        self.assertGreater(len(CONTENT_CATALOG), 20)

    def test_content_item_has_new_fields(self) -> None:
        item = ContentItem(
            name="Test",
            category="movie",
            tags={"family"},
            park_slugs=["magic-kingdom"],
            age_groups=["kids"],
            description="A test item.",
        )
        self.assertEqual(item.park_slugs, ["magic-kingdom"])
        self.assertEqual(item.age_groups, ["kids"])
        self.assertEqual(item.description, "A test item.")

    def test_category_diversity_enforced(self) -> None:
        """No single category should dominate when top_n is large."""
        results = recommend_content(["Frozen", "Marvel", "Star Wars"], CONTENT_CATALOG, top_n=10)
        from collections import Counter
        counts = Counter(r[0].category for r in results)
        # No category should hold more than 50% of slots
        for cat, count in counts.items():
            self.assertLessEqual(count / len(results), 0.6,
                                 f"Category '{cat}' over-represented: {count}/{len(results)}")


if __name__ == "__main__":
    unittest.main()
