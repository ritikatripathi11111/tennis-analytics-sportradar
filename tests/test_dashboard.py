"""Chart builders return Plotly figures (skipped when plotly is not installed)."""
import pandas as pd
import pytest

pytest.importorskip("plotly")

from src.dashboard import charts  # noqa: E402

DF = pd.DataFrame({
    "rank": [1, 2, 3], "name": ["A", "B", "C"], "country": ["Chile", "Spain", "France"],
    "country_code": ["CHL", "ESP", "FRA"], "points": [900, 800, 700], "movement": [0, 1, -1],
    "competitions_played": [20, 18, 25], "competitors": [1, 1, 1],
})


def test_core_charts_build():
    assert charts.top_players_bar(DF).data
    assert charts.rank_points_scatter(DF).data
    assert charts.movement_histogram(DF).data
    assert charts.country_choropleth(DF, "competitors", "t").data
    assert charts.percentile_gauge(60, "p").data
