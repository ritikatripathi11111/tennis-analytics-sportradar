"""Table metadata shared by validation and loading code.

Columns are listed in the same order as in ``schema.sql``.
Max lengths mirror the VARCHAR/CHAR sizes in the project brief.
"""
from __future__ import annotations

TABLE_COLUMNS: dict[str, list[str]] = {
    "categories": ["category_id", "category_name"],
    "competitions": [
        "competition_id", "competition_name", "parent_id",
        "type", "gender", "category_id",
    ],
    "complexes": ["complex_id", "complex_name"],
    "venues": [
        "venue_id", "venue_name", "city_name", "country_name",
        "country_code", "timezone", "complex_id",
    ],
    "competitors": [
        "competitor_id", "name", "country", "country_code", "abbreviation",
    ],
    "competitor_rankings": [
        "rank", "movement", "points", "competitions_played", "competitor_id",
        "tour", "gender", "ranking_year", "ranking_week",
    ],
}

MAX_LENGTHS: dict[str, dict[str, int]] = {
    "categories": {"category_id": 50, "category_name": 100},
    "competitions": {
        "competition_id": 50, "competition_name": 100, "parent_id": 50,
        "type": 20, "gender": 10, "category_id": 50,
    },
    "complexes": {"complex_id": 50, "complex_name": 100},
    "venues": {
        "venue_id": 50, "venue_name": 100, "city_name": 100,
        "country_name": 100, "country_code": 3, "timezone": 100,
        "complex_id": 50,
    },
    "competitors": {
        "competitor_id": 50, "name": 100, "country": 100,
        "country_code": 3, "abbreviation": 10,
    },
    "competitor_rankings": {"competitor_id": 50, "tour": 10, "gender": 10},
}

# Deletion order is the reverse of insertion order (children first).
LOAD_ORDER = [
    "categories", "competitions", "complexes", "venues",
    "competitors", "competitor_rankings",
]
