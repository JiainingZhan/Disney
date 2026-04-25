"""Professional multi-park CLI for the Disney Itinerary Planner."""

import argparse
import sys
from typing import Optional

from .data import DEFAULT_ATTRACTIONS, DEFAULT_SHOWS
from .enrichment_service import EnrichmentService
from .park_config import PARKS, get_park, list_parks
from .planner import build_itinerary


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Disney Itinerary Planner — multi-park intelligent scheduling",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all supported parks
  python -m projects.itinerary_planner.cli --list-parks

  # Show info for a park
  python -m projects.itinerary_planner.cli --park-info magic-kingdom

  # List attractions (with live wait times when available)
  python -m projects.itinerary_planner.cli --park magic-kingdom --list-attractions

  # Generate an optimised itinerary
  python -m projects.itinerary_planner.cli \\
      --park magic-kingdom \\
      --family 0.7 --thrill 0.8 --photo 0.4 \\
      --start 09:00 --hours 8 \\
      --include-vip --show-meals
""",
    )

    # Park selection
    parser.add_argument("--park", metavar="SLUG", help="Park slug (e.g. magic-kingdom, tokyo-disneysea)")
    parser.add_argument("--list-parks", action="store_true", help="List all available parks and exit")
    parser.add_argument("--park-info", metavar="SLUG", help="Show park details and exit")
    parser.add_argument("--list-attractions", action="store_true", help="List attractions for --park and exit")

    # Preference weights
    parser.add_argument("--family", type=float, default=0.6, help="Family preference weight (0–1)")
    parser.add_argument("--thrill", type=float, default=0.6, help="Thrill preference weight (0–1)")
    parser.add_argument("--photo", type=float, default=0.4, help="Photo preference weight (0–1)")

    # Timing
    parser.add_argument("--start", type=str, default="09:00", help="Park entry time HH:MM")
    parser.add_argument("--hours", type=float, default=8.0, help="Available hours in park")

    # Enhanced options
    parser.add_argument("--include-vip", action="store_true", dest="include_vip",
                        help="Prioritise Lightning Lane / FastPass attractions")
    parser.add_argument("--show-meals", action="store_true", dest="show_meals",
                        help="Insert a meal break into the itinerary")

    return parser.parse_args()


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------

def _print_parks() -> None:
    parks = list_parks()
    print(f"{'SLUG':<25} {'NAME':<40} {'LOCATION'}")
    print("-" * 90)
    for p in parks:
        print(f"{p.slug:<25} {p.name:<40} {p.location}")


def _print_park_info(slug: str) -> None:
    park = get_park(slug)
    if park is None:
        print(f"[ERROR] Unknown park slug '{slug}'. Use --list-parks to see available parks.")
        sys.exit(1)
    print(f"\n{'=' * 60}")
    print(f"  {park.name}")
    print(f"{'=' * 60}")
    print(f"  Slug          : {park.slug}")
    print(f"  Location      : {park.location}")
    print(f"  Country       : {park.country}")
    print(f"  Timezone      : {park.timezone}")
    print(f"  Default Hours : {park.default_open} – {park.default_close}")
    print(f"  Description   : {park.description}")
    if park.lands:
        print(f"  Themed Lands  : {', '.join(park.lands)}")
    print()


def _print_attractions(park_slug: str) -> None:
    svc = EnrichmentService()
    attractions = svc.get_attractions(park_slug)
    shows = svc.get_shows(park_slug)

    if not attractions and not shows:
        print(f"No data available for park '{park_slug}'.")
        return

    print(f"\n=== Attractions — {park_slug} ===")
    print(f"{'NAME':<42} {'LAND':<25} {'WAIT':>6} {'TYPE':<14} {'LL'}")
    print("-" * 100)
    for a in sorted(attractions, key=lambda x: x.land):
        ll = "✓" if a.fastpass else " "
        wait = f"{a.wait_min}m"
        hr = f" [{a.height_restriction}]" if a.height_restriction else ""
        print(f"{a.name:<42} {a.land:<25} {wait:>6} {a.attraction_type:<14} {ll}{hr}")

    if shows:
        print(f"\n=== Shows & Entertainment — {park_slug} ===")
        print(f"{'NAME':<42} {'TYPE':<15} {'TIMES'}")
        print("-" * 80)
        seen: set = set()
        for s in shows:
            if s.name not in seen:
                seen.add(s.name)
                time_str = s.start_time.strftime("%H:%M")
                print(f"{s.name:<42} {s.show_type:<15} {time_str}")
    print()


# ---------------------------------------------------------------------------
# Itinerary display
# ---------------------------------------------------------------------------

def _print_itinerary(itinerary, park_slug: Optional[str]) -> None:
    header = f"=== Disney Itinerary"
    if park_slug:
        park = get_park(park_slug)
        if park:
            header += f" — {park.short_name}"
    header += " ==="
    print(header)
    for item in itinerary:
        land_str = f" [{item.land}]" if item.land else ""
        notes_str = f" — {item.notes}" if item.notes else ""
        print(
            f"[{item.item_type:10}] {item.start.strftime('%H:%M')} - {item.end.strftime('%H:%M')}"
            f" | {item.name}{land_str} | score={item.score:.3f}{notes_str}"
        )


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def main() -> None:
    args = parse_args()

    # --list-parks
    if args.list_parks:
        _print_parks()
        return

    # --park-info SLUG
    if args.park_info:
        _print_park_info(args.park_info)
        return

    # --park SLUG --list-attractions
    if args.list_attractions:
        if not args.park:
            print("[ERROR] --list-attractions requires --park SLUG.")
            sys.exit(1)
        _print_attractions(args.park)
        return

    # Build itinerary
    if args.park:
        park_cfg = get_park(args.park)
        if park_cfg is None:
            print(f"[ERROR] Unknown park slug '{args.park}'. Use --list-parks to see available parks.")
            sys.exit(1)
        svc = EnrichmentService()
        attractions = svc.get_attractions(args.park)
        shows = svc.get_shows(args.park)
        if not attractions:
            print(f"[WARNING] No attraction data for '{args.park}', falling back to default data.")
            attractions = DEFAULT_ATTRACTIONS  # type: ignore[assignment]
            shows = DEFAULT_SHOWS  # type: ignore[assignment]
    else:
        attractions = DEFAULT_ATTRACTIONS  # type: ignore[assignment]
        shows = DEFAULT_SHOWS  # type: ignore[assignment]

    itinerary = build_itinerary(
        preferences={"family": args.family, "thrill": args.thrill, "photo": args.photo},
        start_time=args.start,
        available_hours=args.hours,
        attractions=attractions,
        shows=shows,
        include_meal_break=args.show_meals,
        fastpass_priority=args.include_vip,
    )

    if not itinerary:
        print("No feasible itinerary generated with current constraints.")
        return

    _print_itinerary(itinerary, args.park)


if __name__ == "__main__":
    main()
