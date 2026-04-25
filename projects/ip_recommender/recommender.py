from collections import defaultdict
import math
from typing import Dict, Iterable, List, Sequence, Set, Tuple

from .data import ContentItem

# 5% boost for park experiences and merchandise to reflect monetization/engagement value.
CATEGORY_BONUS = 0.05
# Limit each category to 50% of the result list to keep recommendation diversity.
MAX_CATEGORY_RATIO = 0.5


IP_TO_TAGS: Dict[str, Set[str]] = {
    "frozen": {"princess", "music", "family", "magic"},
    "marvel": {"hero", "action", "team", "thrill"},
    "toy_story": {"family", "friendship", "animation", "toy"},
    "pirates": {"adventure", "thrill", "sea", "action"},
    "princess": {"princess", "family", "magic", "photo"},
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


def _candidate_score(user_tags: Set[str], item: ContentItem) -> float:
    overlap = user_tags.intersection(item.tags)
    if not user_tags:
        return 0.0
    overlap_ratio = len(overlap) / len(user_tags)
    category_bonus = CATEGORY_BONUS if item.category in {"park_experience", "merch"} else 0.0
    return overlap_ratio + category_bonus


def recommend_content(
    liked_ips: Sequence[str], catalog: Iterable[ContentItem], top_n: int = 5
) -> List[Tuple[ContentItem, float]]:
    user_tags = build_user_profile(liked_ips)
    scored: List[Tuple[ContentItem, float]] = []
    for item in catalog:
        score = _candidate_score(user_tags, item)
        if score > 0:
            scored.append((item, score))

    scored.sort(key=lambda x: x[1], reverse=True)
    if top_n <= 0:
        return []

    # lightweight category diversity
    category_count = defaultdict(int)
    picked: List[Tuple[ContentItem, float]] = []
    for item, score in scored:
        if len(picked) >= top_n:
            break
        # Keep category diversity by capping each category to a portion of top_n.
        if category_count[item.category] >= max(1, math.ceil(top_n * MAX_CATEGORY_RATIO)):
            continue
        picked.append((item, score))
        category_count[item.category] += 1

    # backfill if diversity constraint filtered too much
    if len(picked) < top_n:
        selected_names = {x[0].name for x in picked}
        for item, score in scored:
            if len(picked) >= top_n:
                break
            if item.name in selected_names:
                continue
            picked.append((item, score))

    return picked
