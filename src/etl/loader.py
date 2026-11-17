"""Load validated records into the SQL database."""
"""Load validated DataFrames into the SQL database (idempotent)."""
from __future__ import annotations

from datetime import datetime

import pandas as pd
from sqlalchemy import text
from sqlalchemy.engine import Connection, Engine
from sqlalchemy.exc import SQLAlchemyError

from src.database.connection import DatabaseError
from src.utils.logger import get_logger

log = get_logger(__name__)


def _insert(conn: Connection, df: pd.DataFrame, table: str) -> int:
    """Append rows to ``table`` (NaN becomes NULL)."""
    if df.empty:
        return 0
    df.astype(object).where(df.notna(), None).to_sql(
        table, conn, if_exists="append", index=False, chunksize=500
    )
    return len(df)


def _refresh_dimension(conn: Connection, frames: dict[str, pd.DataFrame],
                       parent: str, child: str) -> None:
    """Full refresh of a parent/child pair (children are deleted first)."""
    if parent in frames and child in frames:
        conn.execute(text(f"DELETE FROM {child}"))
        conn.execute(text(f"DELETE FROM {parent}"))
        _insert(conn, frames[parent], parent)
        _insert(conn, frames[child], child)
        log.info("Loaded %s=%d, %s=%d", parent, len(frames[parent]), child, len(frames[child]))


def _load_rankings(conn: Connection, frames: dict[str, pd.DataFrame]) -> None:
    """Replace the weekly snapshots being loaded and upsert competitors."""
    rankings = frames["competitor_rankings"]
    competitors = frames["competitors"]

    snapshots = rankings[["tour", "ranking_year", "ranking_week"]].drop_duplicates()
    for snap in snapshots.itertuples(index=False):
        conn.execute(
            text("DELETE FROM competitor_rankings WHERE tour = :tour "
                 "AND ranking_year = :year AND ranking_week = :week"),
            {"tour": snap.tour, "year": int(snap.ranking_year), "week": int(snap.ranking_week)},
        )

    existing = {row[0] for row in conn.execute(text("SELECT competitor_id FROM competitors"))}
    new_rows = competitors.loc[~competitors["competitor_id"].isin(existing)]
    _insert(conn, new_rows, "competitors")

    updates = competitors.loc[competitors["competitor_id"].isin(existing)]
    if not updates.empty:
        conn.execute(
            text("UPDATE competitors SET name = :name, country = :country, "
                 "country_code = :country_code, abbreviation = :abbreviation "
                 "WHERE competitor_id = :competitor_id"),
            updates.to_dict(orient="records"),
        )
    _insert(conn, rankings, "competitor_rankings")
    log.info("Loaded competitors=%d (new=%d), rankings=%d",
             len(competitors), len(new_rows), len(rankings))


def load_all(engine: Engine, frames: dict[str, pd.DataFrame], data_source: str) -> None:
    """Load every available table inside a single transaction."""
    try:
        with engine.begin() as conn:
            _refresh_dimension(conn, frames, "categories", "competitions")
            _refresh_dimension(conn, frames, "complexes", "venues")
            if "competitor_rankings" in frames:
                _load_rankings(conn, frames)
            conn.execute(
                text("INSERT INTO etl_runs (data_source, loaded_at, competitions_rows, "
                     "venues_rows, rankings_rows) VALUES (:src, :ts, :c, :v, :r)"),
                {
                    "src": data_source,
                    "ts": datetime.now().replace(microsecond=0),
                    "c": len(frames.get("competitions", [])),
                    "v": len(frames.get("venues", [])),
                    "r": len(frames.get("competitor_rankings", [])),
                },
            )
    except SQLAlchemyError as exc:
        raise DatabaseError(f"Database load failed and was rolled back: {exc}") from exc
