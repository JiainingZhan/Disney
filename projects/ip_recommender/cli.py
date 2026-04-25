import argparse

from .data import CONTENT_CATALOG
from .recommender import recommend_content


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Disney IP content recommender")
    parser.add_argument("--likes", nargs="+", required=True, help="Liked IPs, e.g. Frozen Marvel")
    parser.add_argument("--top-n", type=int, default=5, help="Top-N recommendations")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    results = recommend_content(liked_ips=args.likes, catalog=CONTENT_CATALOG, top_n=args.top_n)
    if not results:
        print("No recommendations for current preferences.")
        return

    print("=== Disney IP Recommendations ===")
    for item, score in results:
        tags = ",".join(sorted(item.tags))
        print(f"[{item.category:15}] {item.name:25} score={score:.3f} tags={tags}")


if __name__ == "__main__":
    main()

