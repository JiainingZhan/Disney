"""ThemeParks.wiki API wrapper with intelligent mock-data fallback.

Real API docs: https://api.themeparks.wiki/docs/v1/
All requests are GET-only and require no authentication.
"""

import logging
from typing import Any, Dict, List, Optional
from urllib.request import urlopen, Request
from urllib.error import URLError
import json

from .data_cache import DataCache, get_shared_cache
from .park_config import PARKS, ParkConfig

logger = logging.getLogger(__name__)

_BASE_URL = "https://api.themeparks.wiki/v1"
_REQUEST_TIMEOUT = 8  # seconds

# ---------------------------------------------------------------------------
# Mock / fallback attraction data keyed by park slug
# ---------------------------------------------------------------------------

_MOCK_ATTRACTIONS: Dict[str, List[Dict[str, Any]]] = {
    "magic-kingdom": [
        {
            "id": "mk-space-mountain",
            "name": "Space Mountain",
            "type": "ride",
            "land": "Tomorrowland",
            "wait_min": 45,
            "operational": True,
            "duration_min": 9,
            "height_restriction": "44 inches (112 cm)",
            "fastpass": True,
            "tags": {"thrill": 0.9, "family": 0.5, "photo": 0.5, "indoor": 1.0},
            "description": "A classic indoor roller coaster through the cosmos.",
            "accessibility": ["Wheelchair Transfer", "Audio Description"],
        },
        {
            "id": "mk-pirates",
            "name": "Pirates of the Caribbean",
            "type": "ride",
            "land": "Adventureland",
            "wait_min": 30,
            "operational": True,
            "duration_min": 15,
            "height_restriction": None,
            "fastpass": False,
            "tags": {"thrill": 0.5, "family": 0.9, "photo": 0.5},
            "description": "A swashbuckling boat ride through pirate battles.",
            "accessibility": ["Wheelchair Accessible", "Audio Description"],
        },
        {
            "id": "mk-peter-pan",
            "name": "Peter Pan's Flight",
            "type": "ride",
            "land": "Fantasyland",
            "wait_min": 50,
            "operational": True,
            "duration_min": 3,
            "height_restriction": None,
            "fastpass": True,
            "tags": {"thrill": 0.2, "family": 1.0, "photo": 0.4},
            "description": "Soar over Neverland on a magical pirate ship.",
            "accessibility": ["Wheelchair Transfer"],
        },
        {
            "id": "mk-seven-dwarfs",
            "name": "Seven Dwarfs Mine Train",
            "type": "ride",
            "land": "Fantasyland",
            "wait_min": 60,
            "operational": True,
            "duration_min": 4,
            "height_restriction": "38 inches (97 cm)",
            "fastpass": True,
            "tags": {"thrill": 0.7, "family": 0.9, "photo": 0.7},
            "description": "A family coaster through the diamond mine from Snow White.",
            "accessibility": ["Wheelchair Transfer"],
        },
        {
            "id": "mk-haunted-mansion",
            "name": "Haunted Mansion",
            "type": "ride",
            "land": "Liberty Square",
            "wait_min": 35,
            "operational": True,
            "duration_min": 9,
            "height_restriction": None,
            "fastpass": True,
            "tags": {"thrill": 0.4, "family": 0.8, "photo": 0.6},
            "description": "A doom buggy tour through a ghostly estate.",
            "accessibility": ["Wheelchair Accessible"],
        },
        {
            "id": "mk-tron",
            "name": "TRON Lightcycle / Run",
            "type": "ride",
            "land": "Tomorrowland",
            "wait_min": 75,
            "operational": True,
            "duration_min": 3,
            "height_restriction": "48 inches (122 cm)",
            "fastpass": True,
            "tags": {"thrill": 1.0, "family": 0.4, "photo": 0.6},
            "description": "The fastest coaster in any Disney park — race through the Grid.",
            "accessibility": ["Wheelchair Transfer"],
        },
        {
            "id": "mk-castle-photo",
            "name": "Cinderella Castle Photo Spot",
            "type": "interactive",
            "land": "Main Street U.S.A.",
            "wait_min": 5,
            "operational": True,
            "duration_min": 10,
            "height_restriction": None,
            "fastpass": False,
            "tags": {"thrill": 0.0, "family": 0.7, "photo": 1.0},
            "description": "The iconic backdrop for your best park photos.",
            "accessibility": ["Fully Accessible"],
        },
        {
            "id": "mk-big-thunder",
            "name": "Big Thunder Mountain Railroad",
            "type": "ride",
            "land": "Frontierland",
            "wait_min": 40,
            "operational": True,
            "duration_min": 4,
            "height_restriction": "40 inches (102 cm)",
            "fastpass": True,
            "tags": {"thrill": 0.7, "family": 0.8, "photo": 0.5, "outdoor": 1.0},
            "description": 'The "wildest ride in the wilderness" — a mine train roller coaster.',
            "accessibility": ["Wheelchair Transfer"],
        },
    ],
    "epcot": [
        {
            "id": "ep-guardians",
            "name": "Guardians of the Galaxy: Cosmic Rewind",
            "type": "ride",
            "land": "World Discovery",
            "wait_min": 65,
            "operational": True,
            "duration_min": 5,
            "height_restriction": "42 inches (107 cm)",
            "fastpass": True,
            "tags": {"thrill": 1.0, "family": 0.5, "photo": 0.5, "indoor": 1.0},
            "description": "An omnicoaster that blasts through the cosmos to a '70s soundtrack.",
            "accessibility": ["Wheelchair Transfer"],
        },
        {
            "id": "ep-ratatouille",
            "name": "Remy's Ratatouille Adventure",
            "type": "ride",
            "land": "World Celebration",
            "wait_min": 45,
            "operational": True,
            "duration_min": 5,
            "height_restriction": None,
            "fastpass": True,
            "tags": {"thrill": 0.3, "family": 1.0, "photo": 0.6},
            "description": "Shrink to Remy's size and dash through Gusteau's restaurant.",
            "accessibility": ["Wheelchair Accessible"],
        },
        {
            "id": "ep-frozen",
            "name": "Frozen Ever After",
            "type": "ride",
            "land": "World Showcase",
            "wait_min": 55,
            "operational": True,
            "duration_min": 5,
            "height_restriction": None,
            "fastpass": True,
            "tags": {"thrill": 0.3, "family": 1.0, "photo": 0.7},
            "description": "A gentle boat journey through Arendelle's Winter in Summer celebration.",
            "accessibility": ["Wheelchair Accessible"],
        },
        {
            "id": "ep-test-track",
            "name": "Test Track",
            "type": "ride",
            "land": "World Discovery",
            "wait_min": 40,
            "operational": True,
            "duration_min": 7,
            "height_restriction": "40 inches (102 cm)",
            "fastpass": True,
            "tags": {"thrill": 0.6, "family": 0.7, "photo": 0.4},
            "description": "Design a concept car then put it through high-speed tests.",
            "accessibility": ["Wheelchair Transfer"],
        },
    ],
    "hollywood-studios": [
        {
            "id": "hs-rise",
            "name": "Star Wars: Rise of the Resistance",
            "type": "ride",
            "land": "Star Wars: Galaxy's Edge",
            "wait_min": 80,
            "operational": True,
            "duration_min": 18,
            "height_restriction": "40 inches (102 cm)",
            "fastpass": True,
            "tags": {"thrill": 0.8, "family": 0.6, "photo": 0.8},
            "description": "A monumental multi-sequence adventure deep inside a Star Destroyer.",
            "accessibility": ["Wheelchair Transfer"],
        },
        {
            "id": "hs-tower",
            "name": "The Twilight Zone Tower of Terror",
            "type": "ride",
            "land": "Sunset Boulevard",
            "wait_min": 50,
            "operational": True,
            "duration_min": 11,
            "height_restriction": "40 inches (102 cm)",
            "fastpass": True,
            "tags": {"thrill": 1.0, "family": 0.3, "photo": 0.7},
            "description": "Step into a haunted Hollywood hotel and plunge 13 stories.",
            "accessibility": ["Wheelchair Transfer"],
        },
        {
            "id": "hs-slinky",
            "name": "Slinky Dog Dash",
            "type": "ride",
            "land": "Toy Story Land",
            "wait_min": 60,
            "operational": True,
            "duration_min": 3,
            "height_restriction": "38 inches (97 cm)",
            "fastpass": True,
            "tags": {"thrill": 0.6, "family": 1.0, "photo": 0.6, "outdoor": 1.0},
            "description": "A family coaster that weaves through Andy's backyard as Slinky.",
            "accessibility": ["Wheelchair Transfer"],
        },
    ],
    "animal-kingdom": [
        {
            "id": "ak-avatar",
            "name": "Avatar Flight of Passage",
            "type": "ride",
            "land": "Pandora – The World of Avatar",
            "wait_min": 90,
            "operational": True,
            "duration_min": 5,
            "height_restriction": "44 inches (112 cm)",
            "fastpass": True,
            "tags": {"thrill": 0.9, "family": 0.5, "photo": 0.7},
            "description": "Soar on the back of a mountain banshee over Pandora's bioluminescent landscape.",
            "accessibility": ["Wheelchair Transfer"],
        },
        {
            "id": "ak-expedition",
            "name": "Expedition Everest",
            "type": "ride",
            "land": "Asia",
            "wait_min": 45,
            "operational": True,
            "duration_min": 4,
            "height_restriction": "44 inches (112 cm)",
            "fastpass": True,
            "tags": {"thrill": 0.9, "family": 0.5, "photo": 0.5, "outdoor": 1.0},
            "description": "A high-speed train encounter with the legendary Yeti in the Himalayas.",
            "accessibility": ["Wheelchair Transfer"],
        },
        {
            "id": "ak-safari",
            "name": "Kilimanjaro Safaris",
            "type": "ride",
            "land": "Africa",
            "wait_min": 25,
            "operational": True,
            "duration_min": 18,
            "height_restriction": None,
            "fastpass": True,
            "tags": {"thrill": 0.2, "family": 1.0, "photo": 1.0, "outdoor": 1.0},
            "description": "An open-vehicle safari among free-roaming African wildlife.",
            "accessibility": ["Wheelchair Accessible"],
        },
    ],
    "disneyland": [
        {
            "id": "dl-matterhorn",
            "name": "Matterhorn Bobsleds",
            "type": "ride",
            "land": "Fantasyland",
            "wait_min": 40,
            "operational": True,
            "duration_min": 3,
            "height_restriction": "42 inches (107 cm)",
            "fastpass": False,
            "tags": {"thrill": 0.8, "family": 0.5, "photo": 0.6, "outdoor": 1.0},
            "description": "Twin-track bobsled coaster through an iconic Swiss mountain.",
            "accessibility": ["Wheelchair Transfer"],
        },
        {
            "id": "dl-indiana-jones",
            "name": "Indiana Jones Adventure",
            "type": "ride",
            "land": "Adventureland",
            "wait_min": 55,
            "operational": True,
            "duration_min": 4,
            "height_restriction": "46 inches (117 cm)",
            "fastpass": True,
            "tags": {"thrill": 0.8, "family": 0.6, "photo": 0.5},
            "description": "A turbulent jeep ride through the Temple of the Forbidden Eye.",
            "accessibility": ["Wheelchair Transfer"],
        },
        {
            "id": "dl-pirates",
            "name": "Pirates of the Caribbean",
            "type": "ride",
            "land": "New Orleans Square",
            "wait_min": 20,
            "operational": True,
            "duration_min": 16,
            "height_restriction": None,
            "fastpass": False,
            "tags": {"thrill": 0.5, "family": 0.9, "photo": 0.5},
            "description": "Walt's original classic boat ride — still the best version.",
            "accessibility": ["Wheelchair Accessible"],
        },
    ],
    "tokyo-disneyland": [
        {
            "id": "tdl-pooh",
            "name": "Pooh's Hunny Hunt",
            "type": "ride",
            "land": "Fantasyland",
            "wait_min": 70,
            "operational": True,
            "duration_min": 5,
            "height_restriction": None,
            "fastpass": True,
            "tags": {"thrill": 0.2, "family": 1.0, "photo": 0.7},
            "description": "A trackless, honey-pot adventure unique to Tokyo.",
            "accessibility": ["Wheelchair Accessible"],
        },
        {
            "id": "tdl-monster-inc",
            "name": "Monsters, Inc. Ride & Go Seek!",
            "type": "ride",
            "land": "Tomorrowland",
            "wait_min": 50,
            "operational": True,
            "duration_min": 5,
            "height_restriction": None,
            "fastpass": True,
            "tags": {"thrill": 0.3, "family": 1.0, "photo": 0.6},
            "description": "Tag the monsters with your flashlight in this interactive dark ride.",
            "accessibility": ["Wheelchair Accessible"],
        },
    ],
    "tokyo-disneysea": [
        {
            "id": "tds-journey-center",
            "name": "Journey to the Center of the Earth",
            "type": "ride",
            "land": "Mysterious Island",
            "wait_min": 70,
            "operational": True,
            "duration_min": 5,
            "height_restriction": "43 inches (109 cm)",
            "fastpass": True,
            "tags": {"thrill": 1.0, "family": 0.5, "photo": 0.6},
            "description": "Descend into the volcanic depths of Mysterious Island aboard a Terra Vehicle.",
            "accessibility": ["Wheelchair Transfer"],
        },
        {
            "id": "tds-indiana-jones",
            "name": "Indiana Jones Adventure: Temple of the Crystal Skull",
            "type": "ride",
            "land": "Lost River Delta",
            "wait_min": 55,
            "operational": True,
            "duration_min": 4,
            "height_restriction": "46 inches (117 cm)",
            "fastpass": True,
            "tags": {"thrill": 0.8, "family": 0.6, "photo": 0.5},
            "description": "Race through a booby-trapped temple on an all-terrain vehicle.",
            "accessibility": ["Wheelchair Transfer"],
        },
        {
            "id": "tds-tower",
            "name": "Tower of Terror",
            "type": "ride",
            "land": "American Waterfront",
            "wait_min": 60,
            "operational": True,
            "duration_min": 8,
            "height_restriction": "40 inches (102 cm)",
            "fastpass": True,
            "tags": {"thrill": 1.0, "family": 0.3, "photo": 0.6},
            "description": "The ghostly Hotel Hightower drops you in a supernatural free fall.",
            "accessibility": ["Wheelchair Transfer"],
        },
        {
            "id": "tds-fantasy-springs",
            "name": "Peter Pan's Never Land Adventure",
            "type": "ride",
            "land": "Fantasy Springs",
            "wait_min": 80,
            "operational": True,
            "duration_min": 5,
            "height_restriction": None,
            "fastpass": True,
            "tags": {"thrill": 0.5, "family": 1.0, "photo": 0.8},
            "description": "New in Fantasy Springs — a magical flight over Neverland.",
            "accessibility": ["Wheelchair Transfer"],
        },
    ],
    "disneyland-paris": [
        {
            "id": "dlp-phantom-manor",
            "name": "Phantom Manor",
            "type": "ride",
            "land": "Frontierland",
            "wait_min": 30,
            "operational": True,
            "duration_min": 9,
            "height_restriction": None,
            "fastpass": False,
            "tags": {"thrill": 0.5, "family": 0.8, "photo": 0.7},
            "description": "A haunted mansion reimagined in the Wild West — darker than the US version.",
            "accessibility": ["Wheelchair Accessible"],
        },
        {
            "id": "dlp-big-thunder",
            "name": "Big Thunder Mountain",
            "type": "ride",
            "land": "Frontierland",
            "wait_min": 40,
            "operational": True,
            "duration_min": 4,
            "height_restriction": "40 inches (102 cm)",
            "fastpass": True,
            "tags": {"thrill": 0.8, "family": 0.7, "photo": 0.5, "outdoor": 1.0},
            "description": "The most elaborate Big Thunder Mountain in the world — built on an island.",
            "accessibility": ["Wheelchair Transfer"],
        },
    ],
    "hong-kong-disneyland": [
        {
            "id": "hkdl-hyperspace",
            "name": "Hyperspace Mountain",
            "type": "ride",
            "land": "Tomorrowland",
            "wait_min": 40,
            "operational": True,
            "duration_min": 3,
            "height_restriction": "40 inches (102 cm)",
            "fastpass": False,
            "tags": {"thrill": 0.9, "family": 0.5, "photo": 0.4, "indoor": 1.0},
            "description": "An X-wing battles TIE fighters around you in this Star Wars space coaster.",
            "accessibility": ["Wheelchair Transfer"],
        },
        {
            "id": "hkdl-frozen",
            "name": "Wandering Oaken's Sliding Sleighs",
            "type": "ride",
            "land": "World of Frozen",
            "wait_min": 35,
            "operational": True,
            "duration_min": 3,
            "height_restriction": "38 inches (97 cm)",
            "fastpass": False,
            "tags": {"thrill": 0.5, "family": 1.0, "photo": 0.6},
            "description": "Zip through Arendelle's snowy hills on family-friendly sleighs.",
            "accessibility": ["Wheelchair Transfer"],
        },
    ],
    "shanghai-disneyland": [
        {
            "id": "sdl-tron",
            "name": "TRON Lightcycle Power Run",
            "type": "ride",
            "land": "Tomorrow Wonders",
            "wait_min": 70,
            "operational": True,
            "duration_min": 3,
            "height_restriction": "48 inches (122 cm)",
            "fastpass": True,
            "tags": {"thrill": 1.0, "family": 0.4, "photo": 0.7, "outdoor": 1.0},
            "description": "The original TRON coaster that blazed the trail for Magic Kingdom's.",
            "accessibility": ["Wheelchair Transfer"],
        },
        {
            "id": "sdl-roaring-rapids",
            "name": "Roaring Mountain Rapids",
            "type": "ride",
            "land": "Adventure Isle",
            "wait_min": 35,
            "operational": True,
            "duration_min": 10,
            "height_restriction": "42 inches (107 cm)",
            "fastpass": False,
            "tags": {"thrill": 0.7, "family": 0.8, "photo": 0.5, "outdoor": 1.0},
            "description": "A round-boat rapids ride through Mysterious Island's jungle.",
            "accessibility": ["Wheelchair Transfer"],
        },
        {
            "id": "sdl-zootopia",
            "name": "Zootopia: Hot Pursuit",
            "type": "ride",
            "land": "Zootopia",
            "wait_min": 55,
            "operational": True,
            "duration_min": 5,
            "height_restriction": None,
            "fastpass": True,
            "tags": {"thrill": 0.4, "family": 1.0, "photo": 0.7},
            "description": "Chase through Zootopia with Judy Hopps in this trackless adventure.",
            "accessibility": ["Wheelchair Accessible"],
        },
    ],
}

_MOCK_SHOWS: Dict[str, List[Dict[str, Any]]] = {
    "magic-kingdom": [
        {
            "id": "mk-happily-ever-after",
            "name": "Happily Ever After",
            "type": "fireworks",
            "show_times": ["21:00"],
            "duration_min": 18,
            "land": "Main Street U.S.A.",
            "tags": {"thrill": 0.3, "family": 1.0, "photo": 1.0},
            "description": "Nightly castle fireworks and projection spectacular.",
            "accessibility": ["Audio Description", "Viewing Area"],
        },
        {
            "id": "mk-festival-fantasy",
            "name": "Festival of Fantasy Parade",
            "type": "parade",
            "show_times": ["12:00", "15:00"],
            "duration_min": 12,
            "land": "Main Street U.S.A.",
            "tags": {"thrill": 0.1, "family": 1.0, "photo": 0.9},
            "description": "A stunning daytime parade celebrating Disney stories.",
            "accessibility": ["Viewing Area Available"],
        },
        {
            "id": "mk-storybook",
            "name": "Mickey's Storybook Adventure",
            "type": "musical",
            "show_times": ["12:30", "16:00"],
            "duration_min": 30,
            "land": "Fantasyland",
            "tags": {"thrill": 0.1, "family": 1.0, "photo": 0.6},
            "description": "A live stage show celebrating Mickey Mouse across Disney stories.",
            "accessibility": ["Assistive Listening", "Sign Language (select shows)"],
        },
    ],
    "epcot": [
        {
            "id": "ep-luminous",
            "name": "Luminous The Symphony of Us",
            "type": "fireworks",
            "show_times": ["21:00"],
            "duration_min": 14,
            "land": "World Showcase",
            "tags": {"thrill": 0.2, "family": 1.0, "photo": 1.0},
            "description": "Nighttime spectacular over World Showcase Lagoon.",
            "accessibility": ["Audio Description"],
        },
    ],
    "hollywood-studios": [
        {
            "id": "hs-fantasmic",
            "name": "Fantasmic!",
            "type": "musical",
            "show_times": ["20:00", "22:00"],
            "duration_min": 30,
            "land": "Sunset Boulevard",
            "tags": {"thrill": 0.4, "family": 1.0, "photo": 0.9},
            "description": "Mickey's dream battles nightmarish villains in a water and fire spectacular.",
            "accessibility": ["Assistive Listening", "Audio Description"],
        },
    ],
    "animal-kingdom": [
        {
            "id": "ak-tree-of-life",
            "name": "Tree of Life Awakenings",
            "type": "fireworks",
            "show_times": ["19:00", "20:00", "21:00"],
            "duration_min": 3,
            "land": "Discovery Island",
            "tags": {"thrill": 0.1, "family": 1.0, "photo": 1.0},
            "description": "The Tree of Life glows with bioluminescent life as animals emerge at night.",
            "accessibility": ["Fully Accessible"],
        },
    ],
    "disneyland": [
        {
            "id": "dl-magic-happens",
            "name": "Magic Happens Parade",
            "type": "parade",
            "show_times": ["11:00", "14:30"],
            "duration_min": 20,
            "land": "Main Street U.S.A.",
            "tags": {"thrill": 0.1, "family": 1.0, "photo": 0.9},
            "description": "A vibrant daytime parade celebrating magical Disney moments.",
            "accessibility": ["Viewing Area Available"],
        },
        {
            "id": "dl-wondrous-journeys",
            "name": "Wondrous Journeys",
            "type": "fireworks",
            "show_times": ["21:30"],
            "duration_min": 15,
            "land": "Main Street U.S.A.",
            "tags": {"thrill": 0.2, "family": 1.0, "photo": 1.0},
            "description": "A 100th Anniversary fireworks and projection show over the castle.",
            "accessibility": ["Audio Description"],
        },
    ],
    "tokyo-disneyland": [
        {
            "id": "tdl-jubilation",
            "name": "Jubilation! Parade",
            "type": "parade",
            "show_times": ["14:00"],
            "duration_min": 30,
            "land": "World Bazaar",
            "tags": {"thrill": 0.1, "family": 1.0, "photo": 0.9},
            "description": "Tokyo Disneyland's signature upbeat daytime parade.",
            "accessibility": ["Viewing Area Available"],
        },
    ],
    "tokyo-disneysea": [
        {
            "id": "tds-believe",
            "name": "Believe! Sea of Dreams",
            "type": "fireworks",
            "show_times": ["20:30"],
            "duration_min": 20,
            "land": "Mediterranean Harbor",
            "tags": {"thrill": 0.2, "family": 1.0, "photo": 1.0},
            "description": "Spectacular nighttime show combining drones, fireworks, and floating stages.",
            "accessibility": ["Audio Description"],
        },
    ],
    "disneyland-paris": [
        {
            "id": "dlp-dream-lights",
            "name": "Disney Illuminations",
            "type": "fireworks",
            "show_times": ["22:00"],
            "duration_min": 20,
            "land": "Main Street U.S.A.",
            "tags": {"thrill": 0.2, "family": 1.0, "photo": 1.0},
            "description": "Projection mapping and fireworks illuminate the Sleeping Beauty Castle.",
            "accessibility": ["Audio Description"],
        },
    ],
    "hong-kong-disneyland": [
        {
            "id": "hkdl-momentous",
            "name": "Momentous",
            "type": "fireworks",
            "show_times": ["20:30"],
            "duration_min": 18,
            "land": "Main Street U.S.A.",
            "tags": {"thrill": 0.2, "family": 1.0, "photo": 1.0},
            "description": "Castle of Magical Dreams lights up in this emotion-packed nighttime show.",
            "accessibility": ["Audio Description"],
        },
    ],
    "shanghai-disneyland": [
        {
            "id": "sdl-ignite",
            "name": "Ignite the Dream",
            "type": "fireworks",
            "show_times": ["21:00"],
            "duration_min": 20,
            "land": "Gardens of Imagination",
            "tags": {"thrill": 0.2, "family": 1.0, "photo": 1.0},
            "description": "Nightly fireworks over the Enchanted Storybook Castle.",
            "accessibility": ["Audio Description"],
        },
    ],
}


class ThemeParkClient:
    """Wrapper for the ThemeParks.wiki v1 REST API.

    All methods try the live API first; on any error they fall back to the
    bundled mock data so the system remains functional offline.
    """

    def __init__(self, cache: Optional[DataCache] = None, timeout: int = _REQUEST_TIMEOUT) -> None:
        self._cache = cache if cache is not None else get_shared_cache()
        self._timeout = timeout

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_attractions(self, park_slug: str) -> List[Dict[str, Any]]:
        """Return attraction list for *park_slug* (live or mock)."""
        cache_key = f"attractions:{park_slug}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached  # type: ignore[return-value]

        park_cfg = PARKS.get(park_slug)
        data = None
        if park_cfg and park_cfg.api_entity_id:
            data = self._fetch_live_attractions(park_cfg.api_entity_id, park_slug)

        if data is None:
            data = list(_MOCK_ATTRACTIONS.get(park_slug, []))
            logger.info("Using mock attraction data for park '%s'.", park_slug)

        self._cache.set(cache_key, data)
        return data

    def get_shows(self, park_slug: str) -> List[Dict[str, Any]]:
        """Return show list for *park_slug* (live or mock)."""
        cache_key = f"shows:{park_slug}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached  # type: ignore[return-value]

        # Shows/schedules from live API are merged with mock metadata
        data = list(_MOCK_SHOWS.get(park_slug, []))
        self._cache.set(cache_key, data)
        return data

    def get_live_wait_times(self, park_slug: str) -> Dict[str, int]:
        """Return ``{attraction_id: wait_minutes}`` from the live API.

        Returns an empty dict on any error so callers can fall back gracefully.
        """
        cache_key = f"wait_times:{park_slug}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached  # type: ignore[return-value]

        park_cfg = PARKS.get(park_slug)
        result: Dict[str, int] = {}
        if park_cfg and park_cfg.api_entity_id:
            result = self._fetch_live_wait_times(park_cfg.api_entity_id)

        # Cache wait times for a shorter interval (60 seconds)
        self._cache.set(cache_key, result, ttl=60.0)
        return result

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _http_get(self, url: str) -> Optional[Any]:
        """Perform a GET request; return parsed JSON or None on failure."""
        try:
            req = Request(url, headers={"User-Agent": "Disney-Planner/2.0"})
            with urlopen(req, timeout=self._timeout) as resp:
                return json.loads(resp.read().decode())
        except (URLError, OSError, json.JSONDecodeError, Exception) as exc:  # noqa: BLE001
            logger.debug("API request failed for %s: %s", url, exc)
            return None

    def _fetch_live_attractions(
        self, entity_id: str, park_slug: str
    ) -> Optional[List[Dict[str, Any]]]:
        """Fetch and normalise children from the ThemeParks.wiki API."""
        url = f"{_BASE_URL}/entity/{entity_id}/children"
        raw = self._http_get(url)
        if raw is None or "children" not in raw:
            return None

        mock_lookup = {a["id"]: a for a in _MOCK_ATTRACTIONS.get(park_slug, [])}
        enriched: List[Dict[str, Any]] = []
        for child in raw.get("children", []):
            entity_type = child.get("entityType", "").upper()
            if entity_type not in {"ATTRACTION", "SHOW", "RESTAURANT"}:
                continue
            attraction_id = child.get("id", "")
            fallback = mock_lookup.get(attraction_id, {})
            item: Dict[str, Any] = {
                "id": attraction_id,
                "name": child.get("name", fallback.get("name", "Unknown")),
                "type": "ride" if entity_type == "ATTRACTION" else entity_type.lower(),
                "land": child.get("parentId", fallback.get("land", "")),
                "wait_min": fallback.get("wait_min", 30),
                "operational": True,
                "duration_min": fallback.get("duration_min", 10),
                "height_restriction": fallback.get("height_restriction"),
                "fastpass": fallback.get("fastpass", False),
                "tags": fallback.get("tags", {"thrill": 0.5, "family": 0.5, "photo": 0.3}),
                "description": fallback.get("description", ""),
                "accessibility": fallback.get("accessibility", []),
            }
            enriched.append(item)

        if not enriched:
            return None

        # Overlay live wait times
        wait_times = self._fetch_live_wait_times(entity_id)
        for item in enriched:
            if item["id"] in wait_times:
                item["wait_min"] = wait_times[item["id"]]

        return enriched

    def _fetch_live_wait_times(self, entity_id: str) -> Dict[str, int]:
        """Fetch live queue data from the API."""
        url = f"{_BASE_URL}/entity/{entity_id}/live"
        raw = self._http_get(url)
        if raw is None:
            return {}
        result: Dict[str, int] = {}
        for entry in raw.get("liveData", []):
            eid = entry.get("id", "")
            queue = entry.get("queue", {})
            standby = queue.get("STANDBY", {})
            wait = standby.get("waitTime")
            if eid and isinstance(wait, int):
                result[eid] = wait
        return result
