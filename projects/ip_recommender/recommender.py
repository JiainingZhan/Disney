"""Advanced IP content recommender with park and demographic targeting."""

import math
from collections import defaultdict
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple

from .data import ContentItem

# 5% boost for park experiences and merchandise to reflect engagement value.
CATEGORY_BONUS = 0.05
# Limit each category to 50% of the result list to keep recommendation diversity.
MAX_CATEGORY_RATIO = 0.5
# Bonus for items available at the requested park (10%)
PARK_RELEVANCE_BONUS = 0.10
# Bonus for age group match
AGE_GROUP_BONUS = 0.08


# Keys must stay in normalised form produced by _normalize_like_name (lower_snake_case).
IP_TO_TAGS: Dict[str, Set[str]] = {
    "frozen": {"princess", "music", "family", "magic", "ice", "friendship"},
    "frozen_ii": {"princess", "music", "family", "magic", "nature", "adventure"},
    "marvel": {"hero", "action", "team", "thrill", "sci-fi"},
    "avengers": {"hero", "action", "team", "thrill", "sci-fi"},
    "star_wars": {"sci-fi", "action", "adventure", "hero", "space"},
    "toy_story": {"family", "friendship", "animation", "toy", "adventure"},
    "pirates": {"adventure", "thrill", "sea", "action", "family"},
    "princess": {"princess", "family", "magic", "photo"},
    "moana": {"princess", "ocean", "music", "adventure", "family", "nature"},
    "lion_king": {"family", "music", "adventure", "animals", "nature"},
    "ratatouille": {"family", "food", "adventure", "humor", "friendship"},
    "zootopia": {"family", "animals", "adventure", "mystery", "humor"},
    "black_panther": {"hero", "action", "family", "adventure", "tech"},
    "tron": {"sci-fi", "thrill", "action", "tech", "music"},
    "encanto": {"family", "music", "magic", "culture", "friendship"},
    "mickey": {"family", "classic", "magic", "fun"},
    "iron_man": {"hero", "tech", "action", "thrill"},
    "buzz_lightyear": {"hero", "toy", "space", "family"},
    "avatar": {"nature", "adventure", "sci-fi", "thrill", "immersive"},
    "peter_pan": {"family", "adventure", "magic", "classic"},
    "haunted_mansion": {"thrill", "family", "adventure", "classic"},
}


def _normalize_like_name(name: str) -> str:
    return name.strip().lower().replace(" ", "_")


def build_user_profile(liked_ips: Sequence[str]) -> Set[str]:
    profile: Set[str] = set()
    for raw_name in liked_ips:
        key = _normalize_like_name(raw_name)
        if key in IP_TO_TAGS:
            profile.update(IP_TO_TAGS[key])
        else:
            profile.add(key)
    return profile


def _candidate_score(
    user_tags: Set[str],
    item: ContentItem,
    park_slug: Optional[str] = None,
    age_group: Optional[str] = None,
) -> float:
    """Score a content item against user preferences.

    Incorporates tag overlap, category bonuses, park relevance, and age
    group matching.
    """
    overlap = user_tags.intersection(item.tags)
    if not user_tags:
        return 0.0
    overlap_ratio = len(overlap) / len(user_tags)
    category_bonus = CATEGORY_BONUS if item.category in {"park_experience", "merch", "entertainment"} else 0.0
    park_bonus = 0.0
    if park_slug and hasattr(item, "park_slugs") and park_slug in item.park_slugs:
        park_bonus = PARK_RELEVANCE_BONUS
    age_bonus = 0.0
    if age_group and hasattr(item, "age_groups") and age_group in item.age_groups:
        age_bonus = AGE_GROUP_BONUS
    return overlap_ratio + category_bonus + park_bonus + age_bonus


def recommend_content(
    liked_ips: Sequence[str],
    catalog: Iterable[ContentItem],
    top_n: int = 5,
    park_slug: Optional[str] = None,
    age_group: Optional[str] = None,
    include_experiences: bool = False,
) -> List[Tuple[ContentItem, float]]:
    """Return the top-N recommended content items for the given preferences.

    Parameters
    ----------
    liked_ips:
        List of IP names the user likes (e.g. ``["Frozen", "Marvel"]``).
    catalog:
        Iterable of :class:`~.data.ContentItem` objects to score.
    top_n:
        Maximum number of results.
    park_slug:
        When provided, items available at this park receive a scoring bonus.
    age_group:
        One of ``"kids"``, ``"family"``, ``"teens"``, ``"adults"`` — items
        matching the demographic receive a bonus.
    include_experiences:
        When *True*, park experience and dining categories are explicitly
        included even if their raw score is 0 (park_slug must also be set).
    """
    user_tags = build_user_profile(liked_ips)
    scored: List[Tuple[ContentItem, float]] = []
    for item in catalog:
        score = _candidate_score(user_tags, item, park_slug=park_slug, age_group=age_group)
        # When include_experiences is on, ensure park-specific items appear
        if include_experiences and park_slug and hasattr(item, "park_slugs") and park_slug in item.park_slugs:
            score = max(score, CATEGORY_BONUS)
        if score > 0:
            scored.append((item, score))

    scored.sort(key=lambda x: x[1], reverse=True)
    if top_n <= 0:
        return []

    # Lightweight category diversity
    category_count: Dict[str, int] = defaultdict(int)
    picked: List[Tuple[ContentItem, float]] = []
    max_per_category = max(1, math.ceil(top_n * MAX_CATEGORY_RATIO))
    for item, score in scored:
        if len(picked) >= top_n:
            break
        if category_count[item.category] >= max_per_category:
            continue
        picked.append((item, score))
        category_count[item.category] += 1

    # Backfill if diversity constraint filtered too many results
    if len(picked) < top_n:
        selected_names = {x[0].name for x in picked}
        for item, score in scored:
            if len(picked) >= top_n:
                break
            if item.name in selected_names:
                continue
            picked.append((item, score))

    return picked
