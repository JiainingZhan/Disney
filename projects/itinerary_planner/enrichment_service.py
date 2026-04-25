"""Enrichment service — combines ThemeParks API data with static metadata.

Converts raw API / mock dicts into the typed data models used by the planner,
merging live wait-time overlays and adding computed fields.
"""

from datetime import time
from typing import Dict, List, Optional

from .data import Attraction, Show
from .data_cache import DataCache, get_shared_cache
from .themepark_client import ThemeParkClient


class EnrichmentService:
    """Builds enriched, typed attraction and show objects for a given park."""

    def __init__(
        self,
        client: Optional[ThemeParkClient] = None,
        cache: Optional[DataCache] = None,
    ) -> None:
        self._cache = cache if cache is not None else get_shared_cache()
        self._client = client if client is not None else ThemeParkClient(cache=self._cache)

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------

    def get_attractions(self, park_slug: str) -> List[Attraction]:
        """Return typed, enriched attractions for *park_slug*."""
        cache_key = f"enriched_attractions:{park_slug}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached  # type: ignore[return-value]

        raw_list = self._client.get_attractions(park_slug)
        result = [self._build_attraction(raw) for raw in raw_list if raw.get("operational", True)]
        self._cache.set(cache_key, result)
        return result

    def get_shows(self, park_slug: str) -> List[Show]:
        """Return typed, enriched shows for *park_slug*."""
        cache_key = f"enriched_shows:{park_slug}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached  # type: ignore[return-value]

        raw_list = self._client.get_shows(park_slug)
        result: List[Show] = []
        for raw in raw_list:
            result.extend(self._build_shows(raw))
        self._cache.set(cache_key, result)
        return result

    # ------------------------------------------------------------------
    # Internal conversion helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _build_attraction(raw: Dict) -> Attraction:
        tags: Dict[str, float] = raw.get("tags") or {}
        return Attraction(
            name=raw.get("name", "Unknown Attraction"),
            duration_min=int(raw.get("duration_min") or 10),
            wait_min=int(raw.get("wait_min") or 20),
            crowd_factor=_crowd_factor_from_wait(int(raw.get("wait_min") or 20)),
            tags={k: float(v) for k, v in tags.items()},
            land=raw.get("land") or "",
            attraction_type=raw.get("type") or "ride",
            height_restriction=raw.get("height_restriction"),
            fastpass=bool(raw.get("fastpass", False)),
            description=raw.get("description") or "",
            accessibility=list(raw.get("accessibility") or []),
        )

    @staticmethod
    def _build_shows(raw: Dict) -> List[Show]:
        tags: Dict[str, float] = raw.get("tags") or {}
        shows: List[Show] = []
        for time_str in raw.get("show_times") or []:
            parsed = _parse_time(time_str)
            if parsed is None:
                continue
            shows.append(
                Show(
                    name=raw.get("name", "Show"),
                    start_time=parsed,
                    duration_min=int(raw.get("duration_min") or 20),
                    tags={k: float(v) for k, v in tags.items()},
                    show_type=raw.get("type") or "show",
                    description=raw.get("description") or "",
                    accessibility=list(raw.get("accessibility") or []),
                )
            )
        return shows


# ---------------------------------------------------------------------------
# Utility functions
# ---------------------------------------------------------------------------


def _crowd_factor_from_wait(wait_min: int) -> float:
    """Derive a crowd factor (0.8 – 1.5) from wait time."""
    if wait_min <= 15:
        return 0.8
    if wait_min <= 30:
        return 1.0
    if wait_min <= 60:
        return 1.2
    return 1.5


def _parse_time(time_str: str) -> Optional[time]:
    """Parse 'HH:MM' into a :class:`datetime.time` object."""
    try:
        hour, minute = (int(x) for x in time_str.split(":", 1))
        return time(hour=hour, minute=minute)
    except (ValueError, TypeError):
        return None
