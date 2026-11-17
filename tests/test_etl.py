"""Transform and validation tests on tiny hand-written payloads."""
import pandas as pd

from src.etl.transform import parse_competitions, parse_complexes, parse_rankings
from src.etl.validate import validate_frames

COMPETITIONS = {"competitions": [
    {"id": "c1", "name": "ATP Vienna", "gender": "men", "category": {"id": "k1", "name": "ATP"}},
    {"id": "c2", "name": "ATP Vienna Doubles", "parent_id": "c1", "type": "Doubles", "gender": "men",
     "category": {"id": "k1", "name": "ATP"}},
    {"id": "c2", "name": "duplicate", "category": {"id": "k1", "name": "ATP"}},
]}
COMPLEXES = {"complexes": [{"id": "x1", "name": "Nacional", "venues": [
    {"id": "v1", "name": "Court 1", "city_name": "Santiago", "country_name": "Chile",
     "country_code": "chl", "timezone": "America/Santiago"},
    {"id": "v2", "name": "Court 2"}]}]}
RANKINGS = {"rankings": [{"name": "ATP", "year": 2026, "week": 46, "gender": "men", "competitor_rankings": [
    {"rank": 1, "movement": 0, "points": 7500, "competitions_played": 20,
     "competitor": {"id": "p1", "name": "Pavic, Mate", "country": "Croatia", "country_code": "HRV"}},
    {"rank": 2, "movement": "3", "points": "7000", "competitions_played": 18,
     "competitor": {"id": "p2", "name": "Test, Ann", "country": "Chile", "country_code": "CHL", "abbreviation": "TES"}},
    {"rank": 3, "points": 100, "competitor": {}},
]}]}


def build():
    frames = {}
    frames.update(parse_competitions(COMPETITIONS))
    frames.update(parse_complexes(COMPLEXES))
    frames.update(parse_rankings(RANKINGS))
    return validate_frames(frames)


def test_flattening_and_defaults():
    frames, _ = build()
    comps = frames["competitions"].set_index("competition_id")
    assert comps.loc["c1", "type"] == "unknown" and pd.isna(comps.loc["c1", "parent_id"])
    assert comps.loc["c2", "type"] == "doubles"
    assert frames["venues"].set_index("venue_id").loc["v2", "city_name"] == "Unknown"
    assert frames["venues"].set_index("venue_id").loc["v1", "country_code"] == "CHL"


def test_duplicates_and_orphans_are_removed():
    frames, issues = build()
    assert len(frames["competitions"]) == 2
    assert len(frames["competitor_rankings"]) == 2  # row without competitor id dropped
    assert any("duplicate" in msg for msg in issues)


def test_abbreviation_fallback_and_int_coercion():
    frames, _ = build()
    assert frames["competitors"].set_index("competitor_id").loc["p1", "abbreviation"] == "PAV"
    assert frames["competitor_rankings"]["points"].tolist() == [7500, 7000]
