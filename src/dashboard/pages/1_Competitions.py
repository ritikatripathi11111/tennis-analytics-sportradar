import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))  # make `src` importable

import streamlit as st

from src.dashboard import charts, data, ui

ui.setup_page("Competitions Explorer", "🏆",
              "Navigate categories, competition types and the parent / sub-competition hierarchy")

options = data.competition_filters()
st.sidebar.header("Filters")
categories = st.sidebar.multiselect("Category", options["categories"])
types = st.sidebar.multiselect("Type", options["types"])
genders = st.sidebar.multiselect("Gender", options["genders"])
search = st.sidebar.text_input("Search name", placeholder="e.g. Vienna")

df = data.competitions(categories, types, genders, search)
ui.kpi_row([
    ("Competitions", f"{len(df):,}"),
    ("Categories", f"{df['category_name'].nunique():,}"),
    ("Top-level (no parent)", f"{int(df['parent_id'].isna().sum()):,}"),
    ("Doubles events", f"{int((df['type'] == 'doubles').sum()):,}"),
])
if df.empty:
    st.info("No competitions match the filters.")
    st.stop()

overview, hierarchy, table = st.tabs(["Overview", "Hierarchy explorer", "Data table"])

with overview:
    left, right = st.columns(2)
    per_category = df.groupby("category_name").size().reset_index(name="competitions") \
        .sort_values("competitions", ascending=False)
    left.plotly_chart(charts.bar(per_category, "category_name", "competitions",
                                 "Competitions per category", horizontal=True))
    right.plotly_chart(charts.sunburst(df, ["category_name", "type", "gender"],
                                       "Category > type > gender"))
    left, right = st.columns(2)
    by_type = df.groupby("type").size().reset_index(name="competitions")
    left.plotly_chart(charts.donut(by_type, "type", "competitions", "Singles vs doubles vs mixed"))
    mix = df.groupby(["gender", "type"]).size().reset_index(name="competitions")
    right.plotly_chart(charts.bar(mix, "gender", "competitions", "Gender and type mix", color="type"))

with hierarchy:
    parents = data.parent_competitions()
    if parents.empty:
        st.info("No parent/sub-competition relationships in the data.")
    else:
        choice = st.selectbox("Parent competition", parents["competition_name"])
        pid = parents.loc[parents["competition_name"] == choice, "competition_id"].iloc[0]
        children = data.child_competitions(pid)
        st.write(f"**{choice}** has **{len(children)}** sub-competitions")
        st.dataframe(children, hide_index=True)
        st.caption(f"{len(parents)} parent competitions in total; the average has "
                   f"{parents['sub_competitions'].mean():.1f} children.")

with table:
    ui.paged_table(df.drop(columns=["parent_id"]), "comp", file_name="competitions.csv")
