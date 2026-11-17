"""Insight engine tests (pure pandas)."""
import pandas as pd

from src.dashboard.insights import generate_insights


def frame():
    return pd.DataFrame({
        "rank": [1, 1, 3, 4], "name": ["A", "B", "C", "D"], "country": ["X", "X", "Y", "Z"],
        "points": [900, 900, 700, 500], "movement": [0, 2, -3, 0],
        "competitions_played": [20, 18, 25, 12],
    })


def test_insights_cover_leaders_and_movers():
    text = " ".join(f"{h} {b}" for h, b in generate_insights(frame(), "ATP"))
    assert "A & B" in text and "tied" in text
    assert "Biggest climber" in text and "Biggest drop" in text


def test_empty_frame_returns_nothing():
    assert generate_insights(frame().iloc[0:0]) == []
