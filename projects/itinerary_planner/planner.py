from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Dict, Iterable, List, Optional, Set

from .data import Attraction, Show

SHOW_ARRIVAL_WINDOW_MINUTES = 20
MIN_ATTRACTION_TOTAL_MINUTES = 5
# Buffer between consecutive attractions (walking / transition)
TRANSITION_BUFFER_MINUTES = 5
# Default meal break duration
MEAL_BREAK_MINUTES = 45


@dataclass(frozen=True)
class PlanItem:
    name: str
    item_type: str
    start: datetime
    end: datetime
    score: float
    land: str = ""
    notes: str = ""


def _normalize_preferences(preferences: Dict[str, float]) -> Dict[str, float]:
    keys = ("family", "thrill", "photo")
    raw = {k: max(0.0, float(preferences.get(k, 0.0))) for k in keys}
    total = sum(raw.values())
    if total <= 0:
        return {k: 1.0 / len(keys) for k in keys}
    return {k: v / total for k, v in raw.items()}


def _score(tags: Dict[str, float], preferences: Dict[str, float]) -> float:
    return sum(preferences.get(k, 0.0) * tags.get(k, 0.0) for k in preferences)


def _duration_for_attraction(attraction: Attraction) -> int:
    return int(round(attraction.duration_min + attraction.wait_min * attraction.crowd_factor))


def _to_dt(day: date, time_text: str) -> datetime:
    try:
        hour, minute = [int(x) for x in time_text.split(":", maxsplit=1)]
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid start_time '{time_text}'. Expected format is HH:MM.") from exc
    return datetime.combine(day, datetime.min.time()).replace(hour=hour, minute=minute)


def _land_transition_minutes(land_a: str, land_b: str) -> int:
    """Estimate walking time between two lands (rough heuristic).

    Same land -> 0 min; different land -> TRANSITION_BUFFER_MINUTES.
    """
    if not land_a or not land_b or land_a == land_b:
        return 0
    return TRANSITION_BUFFER_MINUTES


def build_itinerary(
    preferences: Dict[str, float],
    start_time: str,
    available_hours: float,
    attractions: Iterable[Attraction],
    shows: Iterable[Show],
    include_meal_break: bool = False,
    fastpass_priority: bool = False,
) -> List[PlanItem]:
    """Build an optimised park itinerary.

    Parameters
    ----------
    preferences:
        Weights for *family*, *thrill*, and *photo* scoring dimensions.
    start_time:
        Park entry time in ``HH:MM`` format.
    available_hours:
        How many hours the guest has in the park.
    attractions:
        Pool of :class:`~.data.Attraction` objects to schedule.
    shows:
        Pool of :class:`~.data.Show` objects with fixed start times.
    include_meal_break:
        When *True*, a lunch break is inserted around midday.
    fastpass_priority:
        When *True*, FastPass/Lightning Lane attractions are boosted in the
        scoring so they are scheduled earlier (to redeem passes promptly).
    """
    norm_preferences = _normalize_preferences(preferences)
    today = date.today()
    current = _to_dt(today, start_time)
    end_time = current + timedelta(hours=max(0.5, available_hours))

    attraction_pool = list(attractions)
    show_pool = list(shows)
    used_attractions: Set[str] = set()
    timeline: List[PlanItem] = []
    last_land: str = ""

    # Pre-compute midday for optional meal break
    midday = current + timedelta(hours=available_hours / 2)
    meal_scheduled = False

    while current < end_time:
        # ----------------------------------------------------------------
        # Optional meal break around midday
        # ----------------------------------------------------------------
        if (
            include_meal_break
            and not meal_scheduled
            and current >= midday - timedelta(minutes=30)
            and current + timedelta(minutes=MEAL_BREAK_MINUTES) <= end_time
        ):
            meal_end = current + timedelta(minutes=MEAL_BREAK_MINUTES)
            timeline.append(
                PlanItem(
                    name="Meal Break",
                    item_type="meal",
                    start=current,
                    end=meal_end,
                    score=0.0,
                    notes="Recommended: quick-service dining nearby",
                )
            )
            current = meal_end
            meal_scheduled = True
            continue

        # ----------------------------------------------------------------
        # Look for an upcoming show within the arrival window
        # ----------------------------------------------------------------
        next_show: Optional[Show] = None
        next_show_start: Optional[datetime] = None
        for show in show_pool:
            show_start = datetime.combine(today, show.start_time)
            if show.name in {item.name for item in timeline}:
                continue
            if current <= show_start and show_start + timedelta(minutes=show.duration_min) <= end_time:
                if next_show_start is None or show_start < next_show_start:
                    next_show = show
                    next_show_start = show_start

        if (
            next_show is not None
            and next_show_start is not None
            and next_show_start <= current + timedelta(minutes=SHOW_ARRIVAL_WINDOW_MINUTES)
        ):
            score = _score(next_show.tags, norm_preferences)
            timeline.append(
                PlanItem(
                    name=next_show.name,
                    item_type="show",
                    start=next_show_start,
                    end=next_show_start + timedelta(minutes=next_show.duration_min),
                    score=score,
                    notes=getattr(next_show, "show_type", ""),
                )
            )
            current = next_show_start + timedelta(minutes=next_show.duration_min)
            continue

        # ----------------------------------------------------------------
        # Select the best attraction via score/time ratio (greedy)
        # ----------------------------------------------------------------
        best_candidate: Optional[Attraction] = None
        best_ratio: float = 0.0
        for attraction in attraction_pool:
            if attraction.name in used_attractions:
                continue
            total_min = _duration_for_attraction(attraction)
            # Add land transition time
            transition = _land_transition_minutes(last_land, getattr(attraction, "land", ""))
            total_with_transition = total_min + transition
            if total_with_transition < max(1, MIN_ATTRACTION_TOTAL_MINUTES):
                continue
            finish = current + timedelta(minutes=total_with_transition)
            if finish > end_time:
                continue
            score = _score(attraction.tags, norm_preferences)
            # Boost FastPass attractions slightly so they are visited early
            if fastpass_priority and getattr(attraction, "fastpass", False):
                score *= 1.15
            ratio = score / total_with_transition
            if ratio > best_ratio:
                best_ratio = ratio
                best_candidate = attraction

        if best_candidate is None:
            break

        total_min = _duration_for_attraction(best_candidate)
        transition = _land_transition_minutes(last_land, getattr(best_candidate, "land", ""))
        score = _score(best_candidate.tags, norm_preferences)
        start = current + timedelta(minutes=transition)
        end = start + timedelta(minutes=total_min)
        land = getattr(best_candidate, "land", "")
        notes_parts = []
        if getattr(best_candidate, "fastpass", False):
            notes_parts.append("Lightning Lane available")
        if getattr(best_candidate, "height_restriction", None):
            notes_parts.append(f"Height: {best_candidate.height_restriction}")
        timeline.append(
            PlanItem(
                name=best_candidate.name,
                item_type="attraction",
                start=start,
                end=end,
                score=score,
                land=land,
                notes=" | ".join(notes_parts),
            )
        )
        used_attractions.add(best_candidate.name)
        last_land = land
        current = end

    return sorted(timeline, key=lambda item: item.start)
