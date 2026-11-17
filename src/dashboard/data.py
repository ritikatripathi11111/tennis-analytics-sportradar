"""Cached data access for the dashboard (thin wrappers over the repository)."""
from __future__ import annotations

import streamlit as st

from src.database import repository as repo

_cached = st.cache_data(ttl=300, show_spinner=False)

periods = _cached(repo.ranking_periods)
rankings = _cached(repo.get_rankings)
ranking_countries = _cached(repo.ranking_countries)
country_stats = _cached(repo.country_stats)
competitor_history = _cached(repo.competitor_history)
competition_filters = _cached(repo.competition_filters)
competitions = _cached(repo.get_competitions)
parent_competitions = _cached(repo.parent_competitions)
child_competitions = _cached(repo.child_competitions)
venues = _cached(repo.get_venues)
venue_countries = _cached(repo.venue_countries)
last_load = _cached(repo.last_load)
