import argparse

from .data import DEFAULT_ATTRACTIONS, DEFAULT_SHOWS
from .planner import build_itinerary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Disney itinerary intelligent planner MVP")
    parser.add_argument("--family", type=float, default=0.6, help="Family preference weight")
    parser.add_argument("--thrill", type=float, default=0.6, help="Thrill preference weight")
    parser.add_argument("--photo", type=float, default=0.4, help="Photo preference weight")
    parser.add_argument("--start", type=str, default="09:00", help="Start time, format HH:MM")
    parser.add_argument("--hours", type=float, default=8.0, help="Available hours in park")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    itinerary = build_itinerary(
        preferences={"family": args.family, "thrill": args.thrill, "photo": args.photo},
        start_time=args.start,
        available_hours=args.hours,
        attractions=DEFAULT_ATTRACTIONS,
        shows=DEFAULT_SHOWS,
    )

    if not itinerary:
        print("No feasible itinerary generated with current constraints.")
        return

    print("=== Disney Itinerary Timeline ===")
    for item in itinerary:
        print(
            f"[{item.item_type:10}] {item.start.strftime('%H:%M')} - {item.end.strftime('%H:%M')} | "
            f"{item.name} | score={item.score:.3f}"
        )


if __name__ == "__main__":
    main()

