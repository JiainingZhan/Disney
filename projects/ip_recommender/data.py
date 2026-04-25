from dataclasses import dataclass
from typing import List, Set


@dataclass(frozen=True)
class ContentItem:
    name: str
    category: str
    tags: Set[str]


CONTENT_CATALOG: List[ContentItem] = [
    ContentItem("Frozen", "movie", {"princess", "music", "family", "magic"}),
    ContentItem("Elsa", "character", {"princess", "magic", "ice", "family"}),
    ContentItem("Frozen Castle Doll", "merch", {"princess", "toy", "family", "gift"}),
    ContentItem("Marvel Avengers", "movie", {"hero", "action", "team", "thrill"}),
    ContentItem("Iron Man", "character", {"hero", "tech", "action", "thrill"}),
    ContentItem("Marvel Action Figure", "merch", {"hero", "toy", "collector", "action"}),
    ContentItem("Toy Story", "movie", {"family", "friendship", "animation", "toy"}),
    ContentItem("Buzz Lightyear", "character", {"hero", "toy", "space", "family"}),
    ContentItem("Pirates Adventure Ride", "park_experience", {"adventure", "thrill", "family", "photo"}),
    ContentItem("Princess Parade", "park_experience", {"princess", "music", "photo", "family"}),
]

