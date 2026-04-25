from dataclasses import dataclass, field
from datetime import time
from typing import Dict, List, Optional


@dataclass(frozen=True)
class Attraction:
    name: str
    duration_min: int
    wait_min: int
    crowd_factor: float
    tags: Dict[str, float]
    # Enhanced fields (optional so existing callers are unaffected)
    land: str = ""
    attraction_type: str = "ride"
    height_restriction: Optional[str] = None
    fastpass: bool = False
    description: str = ""
    accessibility: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class Show:
    name: str
    start_time: time
    duration_min: int
    tags: Dict[str, float]
    # Enhanced fields (optional so existing callers are unaffected)
    show_type: str = "show"
    description: str = ""
    accessibility: List[str] = field(default_factory=list)


DEFAULT_ATTRACTIONS: List[Attraction] = [
    Attraction(
        name="TRON Lightcycle Power Run",
        duration_min=25,
        wait_min=50,
        crowd_factor=1.2,
        tags={"thrill": 1.0, "family": 0.2, "photo": 0.6},
        land="Tomorrowland",
        attraction_type="ride",
        height_restriction="48 inches (122 cm)",
        fastpass=True,
        description="Race through the Grid as a Lightcycle on the fastest coaster in any Disney park.",
    ),
    Attraction(
        name="Pirates of the Caribbean",
        duration_min=20,
        wait_min=30,
        crowd_factor=1.0,
        tags={"thrill": 0.5, "family": 0.8, "photo": 0.5},
        land="Adventureland",
        attraction_type="ride",
        fastpass=False,
        description="A swashbuckling boat ride through pirate battles.",
    ),
    Attraction(
        name="Peter Pan's Flight",
        duration_min=15,
        wait_min=35,
        crowd_factor=1.1,
        tags={"thrill": 0.2, "family": 1.0, "photo": 0.4},
        land="Fantasyland",
        attraction_type="ride",
        fastpass=True,
        description="Soar over Neverland on a magical pirate ship.",
    ),
    Attraction(
        name="Seven Dwarfs Mine Train",
        duration_min=20,
        wait_min=45,
        crowd_factor=1.15,
        tags={"thrill": 0.7, "family": 0.9, "photo": 0.7},
        land="Fantasyland",
        attraction_type="ride",
        height_restriction="38 inches (97 cm)",
        fastpass=True,
        description="A family coaster through the diamond mine from Snow White.",
    ),
    Attraction(
        name="Castle Photo Spot",
        duration_min=25,
        wait_min=10,
        crowd_factor=0.9,
        tags={"thrill": 0.0, "family": 0.6, "photo": 1.0},
        land="Main Street U.S.A.",
        attraction_type="interactive",
        description="The iconic backdrop for your best park photos.",
    ),
]


DEFAULT_SHOWS: List[Show] = [
    Show(
        name="Mickey's Storybook Adventure",
        start_time=time(hour=12, minute=30),
        duration_min=30,
        tags={"thrill": 0.1, "family": 1.0, "photo": 0.6},
        show_type="musical",
        description="A live stage show celebrating Mickey Mouse across Disney stories.",
    ),
    Show(
        name="Castle Night Spectacular",
        start_time=time(hour=20, minute=0),
        duration_min=25,
        tags={"thrill": 0.3, "family": 0.9, "photo": 1.0},
        show_type="fireworks",
        description="Nightly castle fireworks and projection spectacular.",
    ),
]

