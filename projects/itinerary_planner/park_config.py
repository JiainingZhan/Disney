"""Park configuration and metadata for all major Disney parks globally."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ParkConfig:
    """Metadata for a single Disney park."""

    slug: str
    name: str
    short_name: str
    location: str
    country: str
    timezone: str
    default_open: str
    default_close: str
    description: str
    # ThemeParks.wiki API entity ID — empty string means API not available for this park
    api_entity_id: str
    lands: List[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Park registry — keyed by CLI slug
# ---------------------------------------------------------------------------
PARKS: Dict[str, ParkConfig] = {
    "magic-kingdom": ParkConfig(
        slug="magic-kingdom",
        name="Magic Kingdom Park",
        short_name="Magic Kingdom",
        location="Walt Disney World Resort, Orlando, FL, USA",
        country="USA",
        timezone="America/New_York",
        default_open="09:00",
        default_close="23:00",
        description=(
            "The most magical place on earth — home to Cinderella Castle, "
            "classic Disney characters, and timeless attractions across seven themed lands."
        ),
        api_entity_id="75ea578a-adc8-4116-a54d-dccb60765ef0",
        lands=[
            "Main Street U.S.A.",
            "Adventureland",
            "Frontierland",
            "Liberty Square",
            "Fantasyland",
            "Tomorrowland",
            "Storybook Circus",
        ],
    ),
    "epcot": ParkConfig(
        slug="epcot",
        name="EPCOT",
        short_name="EPCOT",
        location="Walt Disney World Resort, Orlando, FL, USA",
        country="USA",
        timezone="America/New_York",
        default_open="09:00",
        default_close="21:00",
        description=(
            "A festival of human achievement and global culture, featuring "
            "World Showcase pavilions and cutting-edge future-world attractions."
        ),
        api_entity_id="47f90d2c-e191-4239-a466-5892ef59a88b",
        lands=[
            "World Celebration",
            "World Discovery",
            "World Nature",
            "World Showcase",
        ],
    ),
    "hollywood-studios": ParkConfig(
        slug="hollywood-studios",
        name="Disney's Hollywood Studios",
        short_name="Hollywood Studios",
        location="Walt Disney World Resort, Orlando, FL, USA",
        country="USA",
        timezone="America/New_York",
        default_open="09:00",
        default_close="21:00",
        description=(
            "Blockbuster thrills at Star Wars: Galaxy's Edge, Toy Story Land, "
            "Sunset Boulevard, and live entertainment on Hollywood Blvd."
        ),
        api_entity_id="288747d1-8b4f-4a64-867e-ea7c9b27bad8",
        lands=[
            "Hollywood Boulevard",
            "Echo Lake",
            "Grand Avenue",
            "Star Wars: Galaxy's Edge",
            "Toy Story Land",
            "Sunset Boulevard",
            "Animation Courtyard",
        ],
    ),
    "animal-kingdom": ParkConfig(
        slug="animal-kingdom",
        name="Disney's Animal Kingdom Theme Park",
        short_name="Animal Kingdom",
        location="Walt Disney World Resort, Orlando, FL, USA",
        country="USA",
        timezone="America/New_York",
        default_open="08:00",
        default_close="21:00",
        description=(
            "Where wilderness and wonder collide — live animals, Pandora: "
            "The World of Avatar, Africa, Asia, and DinoLand U.S.A."
        ),
        api_entity_id="1c84a229-8862-4648-9c71-378ddd2c7693",
        lands=[
            "The Oasis",
            "Discovery Island",
            "Pandora – The World of Avatar",
            "Africa",
            "Asia",
            "DinoLand U.S.A.",
        ],
    ),
    "disneyland": ParkConfig(
        slug="disneyland",
        name="Disneyland Park",
        short_name="Disneyland",
        location="Disneyland Resort, Anaheim, CA, USA",
        country="USA",
        timezone="America/Los_Angeles",
        default_open="09:00",
        default_close="23:00",
        description=(
            "Walt's original magic — eight themed lands, classic rides, "
            "and the iconic Sleeping Beauty Castle in the heart of Anaheim."
        ),
        api_entity_id="7340550b-c14d-4def-80bb-acbe51f9ffe3",
        lands=[
            "Main Street U.S.A.",
            "Adventureland",
            "New Orleans Square",
            "Critter Country",
            "Star Wars: Galaxy's Edge",
            "Fantasyland",
            "Mickey's Toontown",
            "Tomorrowland",
        ],
    ),
    "tokyo-disneyland": ParkConfig(
        slug="tokyo-disneyland",
        name="Tokyo Disneyland",
        short_name="Tokyo Disneyland",
        location="Tokyo Disney Resort, Urayasu, Chiba, Japan",
        country="Japan",
        timezone="Asia/Tokyo",
        default_open="09:00",
        default_close="21:00",
        description=(
            "Japan's beloved interpretation of classic Disney magic, "
            "featuring impeccable service, unique food, and lovingly crafted themed worlds."
        ),
        api_entity_id="209f4878-54b8-41b4-9f6e-c4dfea0e2c86",
        lands=[
            "World Bazaar",
            "Adventureland",
            "Westernland",
            "Critter Country",
            "Fantasyland",
            "Tomorrowland",
        ],
    ),
    "tokyo-disneysea": ParkConfig(
        slug="tokyo-disneysea",
        name="Tokyo DisneySea",
        short_name="Tokyo DisneySea",
        location="Tokyo Disney Resort, Urayasu, Chiba, Japan",
        country="Japan",
        timezone="Asia/Tokyo",
        default_open="09:00",
        default_close="21:00",
        description=(
            "Often ranked the world's best theme park — a nautical fantasy "
            "spanning seven unique ports of call, from a Mediterranean harbor to the depths of the ocean."
        ),
        api_entity_id="b070cbc5-feaa-4b87-a8c1-f94cca037a18",
        lands=[
            "Mediterranean Harbor",
            "American Waterfront",
            "Port Discovery",
            "Lost River Delta",
            "Arabian Coast",
            "Mermaid Lagoon",
            "Mysterious Island",
            "Fantasy Springs",
        ],
    ),
    "disneyland-paris": ParkConfig(
        slug="disneyland-paris",
        name="Disneyland Park Paris",
        short_name="Disneyland Paris",
        location="Disneyland Paris Resort, Marne-la-Vallée, France",
        country="France",
        timezone="Europe/Paris",
        default_open="10:00",
        default_close="22:00",
        description=(
            "European Disney magic with a distinctive flair — a fairy-tale "
            "castle, immersive lands, and seasonal festivals set near Paris."
        ),
        api_entity_id="e57d4ef5-0e9b-4fe7-b374-b74db87e54da",
        lands=[
            "Main Street U.S.A.",
            "Frontierland",
            "Adventureland",
            "Fantasyland",
            "Discoveryland",
        ],
    ),
    "hong-kong-disneyland": ParkConfig(
        slug="hong-kong-disneyland",
        name="Hong Kong Disneyland",
        short_name="HK Disneyland",
        location="Lantau Island, Hong Kong SAR, China",
        country="China (HK)",
        timezone="Asia/Hong_Kong",
        default_open="10:00",
        default_close="21:00",
        description=(
            "Asia's gateway to the Disney universe — intimate, family-centric, "
            "with unique Castle of Magical Dreams and Marvel-themed lands."
        ),
        api_entity_id="e4b03d07-c9cd-4e84-8b37-0e51a7db5e66",
        lands=[
            "Main Street U.S.A.",
            "Fantasyland",
            "Adventureland",
            "Tomorrowland",
            "Toy Story Land",
            "Grizzly Gulch",
            "Mystic Point",
            "World of Frozen",
            "Marvel Avengers Campus",
        ],
    ),
    "shanghai-disneyland": ParkConfig(
        slug="shanghai-disneyland",
        name="Shanghai Disneyland",
        short_name="Shanghai Disney",
        location="Shanghai Disney Resort, Pudong, Shanghai, China",
        country="China",
        timezone="Asia/Shanghai",
        default_open="09:00",
        default_close="21:00",
        description=(
            "The newest Disney park — boldly original with the largest Disney "
            "castle ever built, six immersive themed lands, and uniquely Chinese storytelling."
        ),
        api_entity_id="ead53ea5-22e5-4095-9a83-8c29e74a73ac",
        lands=[
            "Mickey Avenue",
            "Gardens of Imagination",
            "Adventure Isle",
            "Treasure Cove",
            "Fantasyland",
            "Tomorrow Wonders",
            "Toy Story Land",
            "Zootopia",
        ],
    ),
}


def get_park(slug: str) -> Optional[ParkConfig]:
    """Return park config for *slug*, or None if not found."""
    return PARKS.get(slug.lower())


def list_parks() -> List[ParkConfig]:
    """Return all configured parks in display order."""
    return list(PARKS.values())
