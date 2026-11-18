import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))  # make `src` importable

import streamlit as st

from src.dashboard import charts, data, filters, ui

ui.setup_page("Country-wise Analysis", "🌍", "Which nations produce the most and the strongest doubles players?")

f = filters.ranking_filters("ct", with_country=False)
stats = data.country_stats(f["tour"], f["year"], f["week"])
top_n = st.sidebar.slider("Countries shown in charts", 5, 30, 15)
metric = st.sidebar.selectbox("Rank countries by", ["competitors", "total_points", "avg_points"])

ui.kpi_row([
    ("Countries", f"{len(stats):,}"),
    ("Most players", f"{stats.sort_values('competitors', ascending=False).iloc[0]['country']}"),
    ("Highest total points", f"{stats.sort_values('total_points', ascending=False).iloc[0]['country']}"),
    ("Highest avg points", f"{stats.sort_values('avg_points', ascending=False).iloc[0]['country']}"),
])

ranked = stats.sort_values(metric, ascending=False)
label = metric.replace("_", " ")
left, right = st.columns(2)
left.plotly_chart(charts.bar(ranked.head(top_n), "country", metric, f"Top {top_n} countries by {label}",
                             horizontal=True, height=460))
right.plotly_chart(charts.country_choropleth(stats, metric, f"World view: {label}"))
left, right = st.columns(2)
left.plotly_chart(charts.country_bubble(stats))
right.plotly_chart(charts.country_treemap(stats))

st.subheader("Country table")
ui.paged_table(ranked, "country", file_name="country_stats.csv")

st.subheader("Country drill-down")
country = st.selectbox("Country", ranked["country"])
players = data.rankings(f["tour"], f["year"], f["week"], countries=[country])
st.dataframe(players[["rank", "name", "points", "movement", "competitions_played"]], hide_index=True)
