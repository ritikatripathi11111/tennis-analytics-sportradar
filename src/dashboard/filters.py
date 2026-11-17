"""Reusable Streamlit filter widgets."""
"""Reusable Streamlit sidebar filter widgets."""
from __future__ import annotations

from typing import Any

import streamlit as st

from src.dashboard import data


def ranking_filters(key: str = "rk", with_country: bool = True) -> dict[str, Any]:
    """Tour / year / week selectors plus rank, points, country and name filters."""
    periods = data.periods()
    st.sidebar.header("Filters")
    tour = st.sidebar.selectbox("Tour", sorted(periods["tour"].unique()), key=f"{key}_tour")
    sub = periods[periods["tour"] == tour]
    year = int(st.sidebar.selectbox("Year", sorted(sub["ranking_year"].unique(), reverse=True), key=f"{key}_year"))
    weeks = sorted(sub.loc[sub["ranking_year"] == year, "ranking_week"].unique(), reverse=True)
    week = int(st.sidebar.selectbox("Week", weeks, key=f"{key}_week"))
    gender = sub["gender"].iloc[0]
    st.sidebar.caption(f"Gender: {gender}")

    full = data.rankings(tour, year, week)
    max_rank, max_points = int(full["rank"].max()), int(full["points"].max())
    rank_range = st.sidebar.slider("Rank range", 1, max_rank, (1, min(100, max_rank)), key=f"{key}_rank")
    min_points = st.sidebar.slider("Minimum points", 0, max_points, 0, key=f"{key}_points")
    countries: list[str] = []
    if with_country:
        countries = st.sidebar.multiselect("Country", data.ranking_countries(tour, year, week), key=f"{key}_country")
    search = st.sidebar.text_input("Search competitor", placeholder="e.g. Garcia", key=f"{key}_search")
    return {"tour": tour, "year": year, "week": week, "gender": gender,
            "min_rank": int(rank_range[0]), "max_rank": int(rank_range[1]),
            "min_points": int(min_points), "countries": countries, "search": search,
            "max_points": max_points}

