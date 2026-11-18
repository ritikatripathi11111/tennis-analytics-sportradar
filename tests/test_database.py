"""Schema + query tests on an in-memory SQLite database (stdlib sqlite3 only)."""
import sqlite3
from pathlib import Path

import pandas as pd

from src.database.catalog import load_catalog
from src.etl.transform import parse_competitions, parse_complexes, parse_rankings
from src.etl.validate import validate_frames
from src.utils.helpers import SAMPLE_DIR, read_json

SCHEMA_DIR = Path(__file__).resolve().parents[1] / "src" / "database"


def sample_connection():
    frames = {}
    frames.update(parse_competitions(read_json(SAMPLE_DIR / "competitions.json")))
    frames.update(parse_complexes(read_json(SAMPLE_DIR / "complexes.json")))
    frames.update(parse_rankings(read_json(SAMPLE_DIR / "doubles_rankings.json")))
    frames, _ = validate_frames(frames)
    con = sqlite3.connect(":memory:")
    con.executescript((SCHEMA_DIR / "schema_sqlite.sql").read_text(encoding="utf-8"))
    for table, df in frames.items():
        df.astype(object).where(df.notna(), None).to_sql(table, con, if_exists="append", index=False)
    return con


def test_catalog_has_20_required_queries():
    ids = [q.query_id for q in load_catalog()]
    required = [i for i in ids if i[0] in "CVR"]
    assert len(required) == 20


def test_every_query_executes_on_sample_data():
    con = sample_connection()
    for query in load_catalog():
        params = {name: query.defaults[name] for name in query.parameters}
        result = pd.read_sql_query(query.sql, con, params=params)
        assert isinstance(result, pd.DataFrame), query.query_id


def test_known_answers():
    con = sample_connection()
    catalog = {q.query_id: q for q in load_catalog()}
    nacional = pd.read_sql_query(catalog["V7"].sql, con, params={"complex_name": "Nacional"})
    assert len(nacional) == 2
    top5 = pd.read_sql_query(catalog["R2"].sql, con)
    assert top5["rank"].max() <= 5


def test_latest_view_returns_one_snapshot_per_tour():
    con = sample_connection()
    df = pd.read_sql_query("SELECT DISTINCT tour, ranking_week FROM v_latest_rankings", con)
    assert len(df) == 2
