import unittest

from projects.ip_recommender.data import CONTENT_CATALOG
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


if __name__ == "__main__":
    unittest.main()

