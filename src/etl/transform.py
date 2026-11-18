"""Transform nested SportRadar JSON into flat, table-shaped DataFrames."""
from __future__ import annotations

from typing import Any

import pandas as pd

from src.database.models import TABLE_COLUMNS
from src.utils.helpers import clean_text, safe_int


def _frame(rows: list[dict[str, Any]], table: str) -> pd.DataFrame:
    """Build a DataFrame with the exact column order of ``table``."""
    return pd.DataFrame(rows, columns=TABLE_COLUMNS[table])


def parse_competitions(payload: dict[str, Any]) -> dict[str, pd.DataFrame]:
    """Flatten ``competitions.json`` into categories + competitions."""
    categories: dict[str, str] = {}
    competitions: list[dict[str, Any]] = []

    for item in payload.get("competitions", []) or []:
        category = item.get("category") or {}
        category_id = clean_text(category.get("id"))
        if category_id:
            categories[category_id] = clean_text(category.get("name"), "Unknown")
        competitions.append(
            {
                "competition_id": clean_text(item.get("id")),
                "competition_name": clean_text(item.get("name"), "Unknown"),
                "parent_id": clean_text(item.get("parent_id")),
                "type": (clean_text(item.get("type"), "unknown") or "unknown").lower(),
                "gender": (clean_text(item.get("gender"), "unknown") or "unknown").lower(),
                "category_id": category_id,
            }
        )

    categories_df = _frame(
        [{"category_id": k, "category_name": v} for k, v in categories.items()],
        "categories",
    )
    return {"categories": categories_df, "competitions": _frame(competitions, "competitions")}


def parse_complexes(payload: dict[str, Any]) -> dict[str, pd.DataFrame]:
    """Flatten ``complexes.json`` (complex -> venues[]) into two tables."""
    complexes: list[dict[str, Any]] = []
    venues: list[dict[str, Any]] = []

    for complex_item in payload.get("complexes", []) or []:
        complex_id = clean_text(complex_item.get("id"))
        complexes.append(
            {
                "complex_id": complex_id,
                "complex_name": clean_text(complex_item.get("name"), "Unknown"),
            }
        )
        for venue in complex_item.get("venues", []) or []:
            venues.append(
                {
                    "venue_id": clean_text(venue.get("id")),
                    "venue_name": clean_text(venue.get("name"), "Unknown"),
                    "city_name": clean_text(venue.get("city_name"), "Unknown"),
                    "country_name": clean_text(venue.get("country_name"), "Unknown"),
                    "country_code": clean_text(venue.get("country_code"), "UNK"),
                    "timezone": clean_text(venue.get("timezone"), "Unknown"),
                    "complex_id": complex_id,
                }
            )
    return {"complexes": _frame(complexes, "complexes"), "venues": _frame(venues, "venues")}


def _abbreviation(name: str | None) -> str:
    letters = "".join(ch for ch in (name or "") if ch.isalpha())
    return letters[:3].upper() or "UNK"


def parse_rankings(payload: dict[str, Any]) -> dict[str, pd.DataFrame]:
    """Flatten ``double_competitors_rankings.json`` into competitors + rankings."""
    competitors: dict[str, dict[str, Any]] = {}
    rankings: list[dict[str, Any]] = []

    for ranking in payload.get("rankings", []) or []:
        tour = clean_text(ranking.get("name"), "UNKNOWN").upper()
        gender = (clean_text(ranking.get("gender"), "unknown") or "unknown").lower()
        year = safe_int(ranking.get("year"))
        week = safe_int(ranking.get("week"))

        for row in ranking.get("competitor_rankings", []) or []:
            person = row.get("competitor") or {}
            competitor_id = clean_text(person.get("id"))
            name = clean_text(person.get("name"), "Unknown")
            if competitor_id:
                competitors[competitor_id] = {
                    "competitor_id": competitor_id,
                    "name": name,
                    "country": clean_text(person.get("country"), "Unknown"),
                    "country_code": clean_text(person.get("country_code"), "UNK"),
                    "abbreviation": clean_text(person.get("abbreviation"), _abbreviation(name)),
                }
            rankings.append(
                {
                    "rank": safe_int(row.get("rank")),
                    "movement": safe_int(row.get("movement")),
                    "points": safe_int(row.get("points")),
                    "competitions_played": safe_int(row.get("competitions_played")),
                    "competitor_id": competitor_id,
                    "tour": tour,
                    "gender": gender,
                    "ranking_year": year,
                    "ranking_week": week,
                }
            )

    return {
        "competitors": _frame(list(competitors.values()), "competitors"),
        "competitor_rankings": _frame(rankings, "competitor_rankings"),
    }
