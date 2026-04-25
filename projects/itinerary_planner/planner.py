from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Dict, Iterable, List, Set

from .data import Attraction, Show

SHOW_ARRIVAL_WINDOW_MINUTES = 20
MIN_ATTRACTION_TOTAL_MINUTES = 5


@dataclass(frozen=True)
class PlanItem:
    name: str
    item_type: str
    start: datetime
    end: datetime
    score: float


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


def build_itinerary(
    preferences: Dict[str, float],
    start_time: str,
    available_hours: float,
    attractions: Iterable[Attraction],
    shows: Iterable[Show],
) -> List[PlanItem]:
    norm_preferences = _normalize_preferences(preferences)
    today = date.today()
    current = _to_dt(today, start_time)
    end_time = current + timedelta(hours=max(0.5, available_hours))

    attraction_pool = list(attractions)
    show_pool = list(shows)
    used_attractions: Set[str] = set()
    timeline: List[PlanItem] = []

    while current < end_time:
        next_show = None
        next_show_start = None
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
                )
            )
            current = next_show_start + timedelta(minutes=next_show.duration_min)
            continue

        best_candidate = None
        best_ratio = 0.0
        for attraction in attraction_pool:
            if attraction.name in used_attractions:
                continue
            total_min = _duration_for_attraction(attraction)
            if total_min < max(1, MIN_ATTRACTION_TOTAL_MINUTES):
                continue
            finish = current + timedelta(minutes=total_min)
            if finish > end_time:
                continue
            score = _score(attraction.tags, norm_preferences)
            ratio = score / total_min
            if ratio > best_ratio:
                best_ratio = ratio
                best_candidate = attraction

        if best_candidate is None:
            break

        total_min = _duration_for_attraction(best_candidate)
        score = _score(best_candidate.tags, norm_preferences)
        start = current
        end = current + timedelta(minutes=total_min)
        timeline.append(
            PlanItem(
                name=best_candidate.name,
                item_type="attraction",
                start=start,
                end=end,
                score=score,
            )
        )
        used_attractions.add(best_candidate.name)
        current = end

    return sorted(timeline, key=lambda item: item.start)
