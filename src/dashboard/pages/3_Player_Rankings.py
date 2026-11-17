import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))  # make `src` importable

import streamlit as st

from src.dashboard import charts, data, filters, ui

ui.setup_page("Doubles Player Rankings", "📈", "Search, filter and compare doubles competitors")

f = filters.ranking_filters("rk")
df = data.rankings(f["tour"], f["year"], f["week"], f["min_rank"], f["max_rank"],
                   f["countries"], f["min_points"], f["search"])
st.caption(f"{f['tour']} | {f['gender']} | {f['year']} week {f['week']}")

if df.empty:
    st.info("No competitors match the filters. Widen the rank range or lower the points threshold.")
    st.stop()

ui.kpi_row([
    ("Competitors", f"{len(df):,}"),
    ("Countries", f"{df['country'].nunique():,}"),
    ("Highest points", f"{int(df['points'].max()):,}"),
    ("Avg events played", f"{df['competitions_played'].mean():.1f}"),
])

board, explorer, detail = st.tabs(["Leaderboard", "Analysis", "Competitor detail"])

with board:
    view = df[["rank", "name", "country", "points", "movement", "competitions_played"]]
    config = {
        "points": st.column_config.ProgressColumn("Points", min_value=0, max_value=int(f["max_points"]), format="%d"),
        "movement": st.column_config.NumberColumn("Movement", format="%+d"),
        "competitions_played": st.column_config.NumberColumn("Events played"),
    }
    ui.paged_table(view, "rank", config, "doubles_rankings.csv")
    left, right = st.columns(2)
    left.subheader("Highest points")
    left.dataframe(df.nlargest(10, "points")[["name", "country", "points"]], hide_index=True)
    right.subheader("Stable ranks (no movement)")
    right.dataframe(df[df["movement"] == 0].head(10)[["rank", "name", "country"]], hide_index=True)

with explorer:
    left, right = st.columns(2)
    left.plotly_chart(charts.rank_points_scatter(df))
    right.plotly_chart(charts.movement_histogram(df))
    st.plotly_chart(charts.top_players_bar(df, 15, "Top 15 in the current selection"))

with detail:
    labels = (df["rank"].astype(str) + ". " + df["name"] + " (" + df["country_code"] + ")").reset_index(drop=True)
    pick = st.selectbox("Select a competitor", labels)
    row = df.reset_index(drop=True).iloc[int(labels[labels == pick].index[0])]
    full = data.rankings(f["tour"], f["year"], f["week"])
    percentile = 100 * (full["points"] < row["points"]).mean()
    ui.kpi_row([
        ("Rank", f"#{int(row['rank'])}"),
        ("Movement", f"{int(row['movement']):+d}"),
        ("Points", f"{int(row['points']):,}"),
        ("Events played", f"{int(row['competitions_played'])}"),
        ("Country", f"{row['country']}"),
    ])
    left, right = st.columns(2)
    left.plotly_chart(charts.percentile_gauge(round(percentile, 1), "Points percentile in this tour"))
    history = data.competitor_history(row["competitor_id"])
    if len(history) > 1:
        right.plotly_chart(charts.history_chart(history, "Rank history"))
    else:
        right.info("Only one weekly snapshot is stored. Re-run the collector weekly to build history.")
    events = full["competitions_played"].replace(0, 1)
    per_event = row["points"] / max(int(row["competitions_played"]), 1)
    st.write(f"**{row['name']}** earns **{per_event:,.0f}** points per event "
             f"versus a tour average of **{(full['points'] / events).mean():,.0f}**.")
