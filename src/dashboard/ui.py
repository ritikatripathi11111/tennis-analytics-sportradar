"""Shared page chrome: page config, styling, data checks, KPI cards, tables."""
from __future__ import annotations

import pandas as pd
import streamlit as st

from src.database import repository as repo
from src.database.connection import DatabaseError

CSS = """
<style>
  .block-container {padding-top: 2rem; padding-bottom: 2rem;}
  [data-testid="stMetric"] {background: #F3F7F4; border: 1px solid #DDE8E0; border-radius: 12px; padding: 14px 16px;}
  [data-testid="stMetricLabel"] {color: #475569;}
  [data-testid="stMetricValue"] {color: #0F172A; font-weight: 700;}
  .insight {border-left: 4px solid #16A34A; background: #F8FAF9; padding: 10px 14px; border-radius: 6px; margin-bottom: 10px;}
  .insight b {color: #166534;}
</style>
"""


def setup_page(title: str, icon: str = "🎾", subtitle: str | None = None) -> None:
    """Configure the page, show the header and stop early if the DB is empty."""
    st.set_page_config(page_title=f"{title} | Tennis Analytics", page_icon=icon, layout="wide")
    st.markdown(CSS, unsafe_allow_html=True)
    st.title(f"{icon} {title}")
    if subtitle:
        st.caption(subtitle)
    try:
        ready = repo.has_data()
    except DatabaseError as exc:
        st.error(f"Database unavailable: {exc}")
        st.stop()
    if not ready:
        st.warning("The database is empty. Load data first, then refresh this page.")
        st.code("python main.py all      # SportRadar API -> SQL\npython main.py sample   # offline synthetic demo data", language="bash")
        st.stop()
    _data_source_badge()


def _data_source_badge() -> None:
    try:
        run = repo.last_load()
    except DatabaseError:
        return
    if run.empty:
        return
    source = str(run["data_source"].iloc[0])
    when = str(run["loaded_at"].iloc[0])[:16]
    if source == "sample":
        st.sidebar.warning(f"Synthetic demo data (loaded {when}). Run `python main.py all` for live SportRadar data.")
    else:
        st.sidebar.success(f"Live SportRadar data (loaded {when})")


def kpi_row(items: list[tuple[str, str]]) -> None:
    """Render ``[(label, value), ...]`` as equal-width metric cards."""
    for column, (label, value) in zip(st.columns(len(items)), items):
        column.metric(label, value)


def insight_cards(items: list[tuple[str, str]]) -> None:
    """Render insight headline/body pairs as accented callouts."""
    for headline, body in items:
        st.markdown(f"<div class='insight'><b>{headline}</b><br>{body}</div>", unsafe_allow_html=True)


def paged_table(df: pd.DataFrame, key: str, column_config: dict | None = None,
                file_name: str = "export.csv") -> None:
    """Paginated table with a CSV download of the full filtered result."""
    if df.empty:
        st.info("No rows match the current filters.")
        return
    left, middle, right = st.columns([1, 1, 2])
    size = int(left.selectbox("Rows per page", [10, 25, 50, 100], index=1, key=f"{key}_size"))
    pages = max(1, -(-len(df) // size))
    page = int(middle.number_input("Page", 1, pages, 1, key=f"{key}_page")) if pages > 1 else 1
    start = (page - 1) * size
    st.dataframe(df.iloc[start:start + size], hide_index=True, column_config=column_config)
    st.caption(f"Rows {start + 1:,}-{min(start + size, len(df)):,} of {len(df):,}")
    right.download_button("Download CSV", df.to_csv(index=False).encode("utf-8"),
                          file_name=file_name, mime="text/csv", key=f"{key}_dl")
