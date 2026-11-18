import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))  # make `src` importable

import streamlit as st

from src.dashboard import charts, data, ui

ui.setup_page("Venues & Complexes", "🏟️", "Where tennis is played: complexes, venues, countries and time zones")

st.sidebar.header("Filters")
countries = st.sidebar.multiselect("Country", data.venue_countries())
search = st.sidebar.text_input("Search venue, city or complex")
df = data.venues(countries, search)

ui.kpi_row([
    ("Venues", f"{len(df):,}"),
    ("Complexes", f"{df['complex_name'].nunique():,}"),
    ("Countries", f"{df['country_name'].nunique():,}"),
    ("Time zones", f"{df['timezone'].nunique():,}"),
])
if df.empty:
    st.info("No venues match the filters.")
    st.stop()

per_country = df.groupby(["country_name", "country_code"]).size().reset_index(name="venues") \
    .rename(columns={"country_name": "country"})
per_complex = df.groupby("complex_name").size().reset_index(name="venues") \
    .sort_values("venues", ascending=False)
per_tz = df.groupby("timezone").size().reset_index(name="venues").sort_values("venues", ascending=False)

left, right = st.columns(2)
left.plotly_chart(charts.country_choropleth(per_country, "venues", "Venues by country"))
right.plotly_chart(charts.bar(per_complex.head(15), "complex_name", "venues",
                              "Venues per complex (top 15)", horizontal=True))
left, right = st.columns(2)
left.plotly_chart(charts.bar(per_tz.head(15), "timezone", "venues", "Venues per time zone (top 15)", horizontal=True))
multi = per_complex[per_complex["venues"] > 1]
right.subheader("Complexes with more than one venue")
right.dataframe(multi, hide_index=True)

st.subheader("Complex drill-down")
complex_name = st.selectbox("Complex", sorted(df["complex_name"].dropna().unique()))
st.dataframe(df[df["complex_name"] == complex_name][["venue_name", "city_name", "country_name", "timezone"]],
             hide_index=True)

st.subheader("All venues")
ui.paged_table(df, "venues", file_name="venues.csv")
