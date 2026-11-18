import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))  # make `src` importable

import streamlit as st

from src.dashboard import charts, data, filters, insights, ui

ui.setup_page("Smart Insights", "💡", "Automatically generated, plain-English findings for the selected ranking week")

f = filters.ranking_filters("in", with_country=False)
df = data.rankings(f["tour"], f["year"], f["week"])
ui.insight_cards(insights.generate_insights(df, f["tour"]))

st.subheader("Efficiency leaders (points per event, min. 10 events)")
active = df[df["competitions_played"] >= 10].copy()
active["points_per_event"] = (active["points"] / active["competitions_played"]).round(1)
top = active.nlargest(10, "points_per_event")
st.plotly_chart(charts.bar(top, "name", "points_per_event", "Points per event", horizontal=True))
st.caption("Rule-based analytics (pandas). Extend `src/dashboard/insights.py` with an LLM summary if desired.")
