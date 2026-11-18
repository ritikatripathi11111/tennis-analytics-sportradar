"""Reusable, parameterised read queries for the dashboard (no Streamlit here)."""
from __future__ import annotations

from typing import Any, Iterable

import pandas as pd
from sqlalchemy import bindparam, text
from sqlalchemy.exc import SQLAlchemyError

from src.database.catalog import CatalogQuery
from src.database.connection import DatabaseError, get_engine


def read_sql(sql: str, params: dict[str, Any] | None = None,
             expanding: Iterable[str] = ()) -> pd.DataFrame:
    """Run a SELECT and return a DataFrame. ``expanding`` lists IN-list params."""
    statement = text(sql)
    names = list(expanding)
    if names:
        statement = statement.bindparams(*[bindparam(n, expanding=True) for n in names])
    try:
        with get_engine().connect() as conn:
            return pd.read_sql_query(statement, conn, params=params or {})
    except SQLAlchemyError as exc:
        raise DatabaseError(f"Query failed: {exc}") from exc


# --------------------------------------------------------------------- status
def has_data() -> bool:
    """True when the rankings table exists and contains rows."""
    get_engine()  # connection problems must surface, not look like "no data"
    try:
        return int(read_sql("SELECT COUNT(*) AS n FROM competitor_rankings")["n"][0]) > 0
    except DatabaseError:  # table does not exist yet
        return False


def last_load() -> pd.DataFrame:
    """Most recent ETL run (source and timestamp)."""
    return read_sql("SELECT data_source, loaded_at FROM etl_runs ORDER BY run_id DESC LIMIT 1")


# -------------------------------------------------------------------- rankings
def ranking_periods() -> pd.DataFrame:
    """Every available (tour, gender, year, week) snapshot."""
    return read_sql(
        "SELECT DISTINCT tour, gender, ranking_year, ranking_week "
        "FROM competitor_rankings ORDER BY tour, ranking_year DESC, ranking_week DESC"
    )


def ranking_countries(tour: str, year: int, week: int) -> list[str]:
    """Countries present in one ranking snapshot."""
    df = read_sql(
        "SELECT DISTINCT cp.country FROM competitor_rankings r "
        "JOIN competitors cp ON cp.competitor_id = r.competitor_id "
        "WHERE r.tour = :tour AND r.ranking_year = :year AND r.ranking_week = :week "
        "ORDER BY cp.country",
        {"tour": tour, "year": year, "week": week},
    )
    return df["country"].tolist()


def get_rankings(tour: str, year: int, week: int, min_rank: int = 1, max_rank: int = 10_000,
                 countries: list[str] | None = None, min_points: int = 0,
                 search: str = "") -> pd.DataFrame:
    """Filtered ranking rows (filters are applied in SQL)."""
    sql = (
        "SELECT r.`rank`, cp.name, cp.country, cp.country_code, cp.abbreviation, r.points, "
        "r.movement, r.competitions_played, r.tour, r.gender, r.ranking_year, r.ranking_week, "
        "cp.competitor_id "
        "FROM competitor_rankings r JOIN competitors cp ON cp.competitor_id = r.competitor_id "
        "WHERE r.tour = :tour AND r.ranking_year = :year AND r.ranking_week = :week "
        "AND r.`rank` BETWEEN :min_rank AND :max_rank AND r.points >= :min_points"
    )
    params: dict[str, Any] = {"tour": tour, "year": year, "week": week,
                              "min_rank": min_rank, "max_rank": max_rank, "min_points": min_points}
    expanding: list[str] = []
    if countries:
        sql += " AND cp.country IN :countries"
        params["countries"] = list(countries)
        expanding.append("countries")
    if search.strip():
        sql += " AND LOWER(cp.name) LIKE :search"
        params["search"] = f"%{search.strip().lower()}%"
    sql += " ORDER BY r.`rank`, cp.name"
    return read_sql(sql, params, expanding)


def country_stats(tour: str, year: int, week: int) -> pd.DataFrame:
    """Competitors, total/average points and best rank per country."""
    return read_sql(
        "SELECT cp.country, cp.country_code, COUNT(*) AS competitors, "
        "SUM(r.points) AS total_points, ROUND(AVG(r.points), 1) AS avg_points, "
        "MIN(r.`rank`) AS best_rank "
        "FROM competitor_rankings r JOIN competitors cp ON cp.competitor_id = r.competitor_id "
        "WHERE r.tour = :tour AND r.ranking_year = :year AND r.ranking_week = :week "
        "GROUP BY cp.country, cp.country_code ORDER BY competitors DESC, total_points DESC",
        {"tour": tour, "year": year, "week": week},
    )


def competitor_history(competitor_id: str) -> pd.DataFrame:
    """All stored weekly snapshots for one competitor."""
    return read_sql(
        "SELECT ranking_year, ranking_week, `rank`, points, movement, competitions_played "
        "FROM competitor_rankings WHERE competitor_id = :cid "
        "ORDER BY ranking_year, ranking_week",
        {"cid": competitor_id},
    )


# ---------------------------------------------------------------- competitions
def competition_filters() -> dict[str, list[str]]:
    """Distinct values for the competitions filter widgets."""
    return {
        "categories": read_sql("SELECT category_name FROM categories ORDER BY category_name")["category_name"].tolist(),
        "types": read_sql("SELECT DISTINCT type FROM competitions ORDER BY type")["type"].tolist(),
        "genders": read_sql("SELECT DISTINCT gender FROM competitions ORDER BY gender")["gender"].tolist(),
    }


def get_competitions(categories: list[str] | None = None, types: list[str] | None = None,
                     genders: list[str] | None = None, search: str = "") -> pd.DataFrame:
    """Competitions with their category name, filtered in SQL."""
    sql = (
        "SELECT c.competition_id, c.competition_name, c.type, c.gender, c.parent_id, "
        "COALESCE(cat.category_name, 'Uncategorised') AS category_name "
        "FROM competitions c LEFT JOIN categories cat ON cat.category_id = c.category_id WHERE 1 = 1"
    )
    params: dict[str, Any] = {}
    expanding: list[str] = []
    for column, key, values in (("cat.category_name", "categories", categories),
                                ("c.type", "types", types), ("c.gender", "genders", genders)):
        if values:
            sql += f" AND {column} IN :{key}"
            params[key] = list(values)
            expanding.append(key)
    if search.strip():
        sql += " AND LOWER(c.competition_name) LIKE :search"
        params["search"] = f"%{search.strip().lower()}%"
    return read_sql(sql + " ORDER BY category_name, c.competition_name", params, expanding)


def parent_competitions() -> pd.DataFrame:
    """Parent competitions with their number of sub-competitions."""
    return read_sql(
        "SELECT p.competition_id, p.competition_name, COUNT(ch.competition_id) AS sub_competitions "
        "FROM competitions p JOIN competitions ch ON ch.parent_id = p.competition_id "
        "GROUP BY p.competition_id, p.competition_name ORDER BY p.competition_name"
    )


def child_competitions(parent_id: str) -> pd.DataFrame:
    """Sub-competitions of one parent."""
    return read_sql(
        "SELECT competition_id, competition_name, type, gender FROM competitions "
        "WHERE parent_id = :pid ORDER BY competition_name",
        {"pid": parent_id},
    )


# ---------------------------------------------------------------------- venues
def get_venues(countries: list[str] | None = None, search: str = "") -> pd.DataFrame:
    """Venues with complex name, filtered in SQL."""
    sql = (
        "SELECT v.venue_id, v.venue_name, v.city_name, v.country_name, v.country_code, "
        "v.timezone, cx.complex_name FROM venues v "
        "LEFT JOIN complexes cx ON cx.complex_id = v.complex_id WHERE 1 = 1"
    )
    params: dict[str, Any] = {}
    expanding: list[str] = []
    if countries:
        sql += " AND v.country_name IN :countries"
        params["countries"] = list(countries)
        expanding.append("countries")
    if search.strip():
        sql += " AND (LOWER(v.venue_name) LIKE :search OR LOWER(v.city_name) LIKE :search " \
               "OR LOWER(cx.complex_name) LIKE :search)"
        params["search"] = f"%{search.strip().lower()}%"
    return read_sql(sql + " ORDER BY v.country_name, v.city_name, v.venue_name", params, expanding)


def venue_countries() -> list[str]:
    """Distinct venue countries."""
    return read_sql("SELECT DISTINCT country_name FROM venues ORDER BY country_name")["country_name"].tolist()


# ------------------------------------------------------------------ SQL lab
def run_catalog_query(query: CatalogQuery, params: dict[str, str] | None = None) -> pd.DataFrame:
    """Execute one query from queries.sql with user-supplied parameter values."""
    values = {name: (params or {}).get(name, query.defaults.get(name, "")) for name in query.parameters}
    return read_sql(query.sql, values)
