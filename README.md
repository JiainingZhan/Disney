# ✨ Disney Project Suite

> Intelligent theme park experience optimizer with modular architecture and extensible design

This repository contains two Disney-themed projects: (1) an intelligent park itinerary planner MVP and (2) a Disney IP content recommender, with runnable CLIs, tests, and extensible architecture.

---

## Project Overview

- **Main Project**: Disney Park Itinerary Intelligent Planning Platform (MVP)
- **Secondary Project**: Disney IP Content Recommendation System

Design Goals: Modular architecture, demonstrable business logic, clear test coverage.

---

## Directory Structure

```text
projects/
  itinerary_planner/
    data.py
    planner.py
    cli.py
  ip_recommender/
    data.py
    recommender.py
    cli.py
tests/
  test_itinerary_planner.py
  test_ip_recommender.py
```

---

## Main Project: Disney Park Itinerary Planning Platform (MVP)

### Implemented Features

- User preference input (family-friendly / thrill / photography)
- Park entry time and available duration
- Automatic itinerary generation based on queue time, crowd factors, and preference scoring
- Show attractions (fixed start times) automatically inserted into itinerary
- Results output as structured timeline

### Core Algorithm

- Attractions: Priority calculated by "preference score / estimated duration", greedy selection
- Shows: Fixed time windows, prioritized insertion if time permits
- Final Output: Time-ordered structured itinerary

### Usage Example

```bash
python -m projects.itinerary_planner.cli \
  --family 0.7 --thrill 0.8 --photo 0.4 \
  --start 09:00 --hours 8
```

---

## Secondary Project: Disney IP Content Recommendation System

### Implemented Features

- User input of favorite IPs (e.g., Frozen, Marvel)
- Candidate scoring based on tag overlap and category matching
- Output Top-N recommended content (movies / characters / merchandise / park experiences)

### Core Algorithm

- Unified tag system (characters, style, age group, type, etc.)
- Score calculation based on user preference tags and candidate content tag overlap
- Category light weighting to avoid recommendation homogeneity

### Usage Example

```bash
python -m projects.ip_recommender.cli \
  --likes Frozen Marvel \
  --top-n 5
```

---

## Testing

```bash
python -m unittest discover -s tests -v
```

---

## Design Rationale

- **Itinerary Planning Value**: Automated parsing of user preferences and spatio-temporal constraints to generate executable itineraries
- **Technical Strategy**: Interpretable rule-based + scoring model (MVP phase) for easy debugging and iteration
- **Metrics Example**: Itinerary generation time, preference match rate, show coverage rate

---

## Future Extensibility

- Integration with real-time queue and show schedule APIs
- Itinerary planning upgrade from greedy to dynamic programming / heuristic search
- Recommendation system upgrade from rule-based to collaborative filtering / vector recall
- Add web frontend and visualization dashboard
