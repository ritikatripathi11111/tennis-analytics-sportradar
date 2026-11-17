import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # make `src` importable

import streamlit as st

from src.dashboard import charts, data, insights, ui
from src.database import repository as repo

ui.setup_page("Tennis Analytics Command Center", "🎾",
              "Doubles rankings, competition structure and venues from the SportRadar Tennis API")

periods = data.periods()
tour = st.radio("Tour", sorted(periods["tour"].unique()), horizontal=True)
latest = periods[periods["tour"] == tour].iloc[0]
year, week = int(latest["ranking_year"]), int(latest["ranking_week"])
df = data.rankings(tour, year, week)
countries = data.country_stats(tour, year, week)
st.caption(f"{tour} doubles rankings | {latest['gender']} | {year} week {week}")

comp_total = int(repo.read_sql("SELECT COUNT(*) AS n FROM competitions")["n"][0])
venue_total = int(repo.read_sql("SELECT COUNT(*) AS n FROM venues")["n"][0])
ui.kpi_row([
    ("Total competitors", f"{len(df):,}"),
    ("Countries represented", f"{df['country'].nunique():,}"),
    ("Highest points", f"{int(df['points'].max()):,}"),
    ("Average points", f"{df['points'].mean():,.0f}"),
    ("Competitions tracked", f"{comp_total:,}"),
    ("Venues tracked", f"{venue_total:,}"),
])

st.divider()
left, right = st.columns(2)
left.plotly_chart(charts.top_players_bar(df, 10, f"Top 10 {tour} players by points"))
right.plotly_chart(charts.country_choropleth(countries, "competitors", "Where the ranked players come from"))

left, right = st.columns(2)
left.plotly_chart(charts.rank_points_scatter(df))
right.plotly_chart(charts.movement_histogram(df))

st.subheader("Key insights")
ui.insight_cards(insights.generate_insights(df, tour)[:4])
st.caption("Use the sidebar pages for competitions, venues, rankings, country analysis, more insights and the SQL query lab.")
