"""Professional IP recommender CLI with park and demographic targeting."""

import argparse
import sys

from .data import CONTENT_CATALOG
from .recommender import recommend_content


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Disney IP Content Recommender — advanced multi-park matching",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic recommendation
  python -m projects.ip_recommender.cli --likes Frozen Marvel --top-n 5

  # With park context and experience inclusion
  python -m projects.ip_recommender.cli \\
      --likes Frozen Marvel \\
      --park magic-kingdom \\
      --top-n 10 \\
      --include-experiences

  # Demographic targeting
  python -m projects.ip_recommender.cli \\
      --likes "Star Wars" "Toy Story" \\
      --age-group family \\
      --top-n 8
""",
    )
    parser.add_argument("--likes", nargs="+", required=True, help="Liked IPs, e.g. Frozen Marvel")
    parser.add_argument("--top-n", type=int, default=5, help="Top-N recommendations")
    parser.add_argument("--park", metavar="SLUG", default=None,
                        help="Park slug for park-specific scoring (e.g. magic-kingdom)")
    parser.add_argument("--age-group", metavar="GROUP", default=None,
                        choices=["kids", "family", "teens", "adults"],
                        help="Demographic targeting: kids / family / teens / adults")
    parser.add_argument("--include-experiences", action="store_true", dest="include_experiences",
                        help="Include park experiences and dining in results")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    results = recommend_content(
        liked_ips=args.likes,
        catalog=CONTENT_CATALOG,
        top_n=args.top_n,
        park_slug=args.park,
        age_group=args.age_group,
        include_experiences=args.include_experiences,
    )
    if not results:
        print("No recommendations for current preferences.")
        return

    header = "=== Disney IP Recommendations ==="
    if args.park:
        header = f"=== Disney IP Recommendations — {args.park} ==="
    print(header)
    for item, score in results:
        tags = ",".join(sorted(item.tags))
        park_note = ""
        if args.park and hasattr(item, "park_slugs") and args.park in item.park_slugs:
            park_note = " [available at park]"
        print(f"[{item.category:15}] {item.name:30} score={score:.3f} tags={tags}{park_note}")


if __name__ == "__main__":
    main()
