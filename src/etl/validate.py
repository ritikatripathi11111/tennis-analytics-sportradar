"""Validate required fields and relationships before loading."""
"""Validate required fields, lengths and relationships before loading."""
from __future__ import annotations

import pandas as pd

from src.database.models import MAX_LENGTHS
from src.utils.logger import get_logger

log = get_logger(__name__)

PRIMARY_KEYS = {
    "categories": ["category_id"],
    "competitions": ["competition_id"],
    "complexes": ["complex_id"],
    "venues": ["venue_id"],
    "competitors": ["competitor_id"],
    "competitor_rankings": ["tour", "ranking_year", "ranking_week", "competitor_id"],
}


def _truncate(df: pd.DataFrame, table: str, issues: list[str]) -> pd.DataFrame:
    """Trim text columns to the VARCHAR/CHAR sizes defined by the schema."""
    for column, limit in MAX_LENGTHS.get(table, {}).items():
        if column not in df.columns:
            continue
        too_long = df[column].notna() & (df[column].astype(str).str.len() > limit)
        if too_long.any():
            issues.append(f"{table}.{column}: truncated {int(too_long.sum())} value(s) to {limit} chars")
            df.loc[too_long, column] = df.loc[too_long, column].astype(str).str[:limit]
    if table in ("venues", "competitors") and "country_code" in df.columns:
        df["country_code"] = df["country_code"].astype(str).str.upper()
    return df


def _drop_missing_keys(df: pd.DataFrame, table: str, issues: list[str]) -> pd.DataFrame:
    keys = PRIMARY_KEYS[table]
    missing = df[keys].isna().any(axis=1)
    if missing.any():
        issues.append(f"{table}: dropped {int(missing.sum())} row(s) with missing key")
    return df.loc[~missing]


def _drop_duplicates(df: pd.DataFrame, table: str, issues: list[str]) -> pd.DataFrame:
    sort_cols = ["rank"] if table == "competitor_rankings" else None
    if sort_cols:
        df = df.sort_values(sort_cols)  # keep the best rank for duplicate players
    dup = df.duplicated(subset=PRIMARY_KEYS[table], keep="first")
    if dup.any():
        issues.append(f"{table}: removed {int(dup.sum())} duplicate row(s)")
    return df.loc[~dup]


def validate_frames(
    frames: dict[str, pd.DataFrame],
) -> tuple[dict[str, pd.DataFrame], list[str]]:
    """Clean every table and enforce foreign keys.

    Returns the cleaned frames plus a human-readable list of data-quality issues.
    """
    issues: list[str] = []
    clean: dict[str, pd.DataFrame] = {}

    for table, df in frames.items():
        df = df.copy()
        df = _drop_missing_keys(df, table, issues)
        df = _drop_duplicates(df, table, issues)
        df = _truncate(df, table, issues)
        clean[table] = df.reset_index(drop=True)

    # Foreign keys -------------------------------------------------------
    if {"categories", "competitions"} <= clean.keys():
        known = set(clean["categories"]["category_id"])
        bad = clean["competitions"]["category_id"].notna() & ~clean["competitions"]["category_id"].isin(known)
        if bad.any():
            issues.append(f"competitions: nulled {int(bad.sum())} unknown category_id")
            clean["competitions"].loc[bad, "category_id"] = None

    if {"complexes", "venues"} <= clean.keys():
        known = set(clean["complexes"]["complex_id"])
        bad = ~clean["venues"]["complex_id"].isin(known)
        if bad.any():
            issues.append(f"venues: dropped {int(bad.sum())} row(s) without a valid complex")
            clean["venues"] = clean["venues"].loc[~bad].reset_index(drop=True)

    if {"competitors", "competitor_rankings"} <= clean.keys():
        known = set(clean["competitors"]["competitor_id"])
        bad = ~clean["competitor_rankings"]["competitor_id"].isin(known)
        if bad.any():
            issues.append(f"competitor_rankings: dropped {int(bad.sum())} orphan row(s)")
            clean["competitor_rankings"] = clean["competitor_rankings"].loc[~bad].reset_index(drop=True)

    for message in issues:
        log.warning(message)
    return clean, issues
