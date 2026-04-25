from dataclasses import dataclass
from datetime import time
from typing import Dict, List


@dataclass(frozen=True)
class Attraction:
    name: str
    duration_min: int
    wait_min: int
    crowd_factor: float
    tags: Dict[str, float]


@dataclass(frozen=True)
class Show:
    name: str
    start_time: time
    duration_min: int
    tags: Dict[str, float]


DEFAULT_ATTRACTIONS: List[Attraction] = [
    Attraction(
        name="TRON Lightcycle Power Run",
        duration_min=25,
        wait_min=50,
        crowd_factor=1.2,
        tags={"thrill": 1.0, "family": 0.2, "photo": 0.6},
    ),
    Attraction(
        name="Pirates of the Caribbean",
        duration_min=20,
        wait_min=30,
        crowd_factor=1.0,
        tags={"thrill": 0.5, "family": 0.8, "photo": 0.5},
    ),
    Attraction(
        name="Peter Pan's Flight",
        duration_min=15,
        wait_min=35,
        crowd_factor=1.1,
        tags={"thrill": 0.2, "family": 1.0, "photo": 0.4},
    ),
    Attraction(
        name="Seven Dwarfs Mine Train",
        duration_min=20,
        wait_min=45,
        crowd_factor=1.15,
        tags={"thrill": 0.7, "family": 0.9, "photo": 0.7},
    ),
    Attraction(
        name="Castle Photo Spot",
        duration_min=25,
        wait_min=10,
        crowd_factor=0.9,
        tags={"thrill": 0.0, "family": 0.6, "photo": 1.0},
    ),
]


DEFAULT_SHOWS: List[Show] = [
    Show(
        name="Mickey's Storybook Adventure",
        start_time=time(hour=12, minute=30),
        duration_min=30,
        tags={"thrill": 0.1, "family": 1.0, "photo": 0.6},
    ),
    Show(
        name="Castle Night Spectacular",
        start_time=time(hour=20, minute=0),
        duration_min=25,
        tags={"thrill": 0.3, "family": 0.9, "photo": 1.0},
    ),
]

