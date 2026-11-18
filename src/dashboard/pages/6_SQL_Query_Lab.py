import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))  # make `src` importable

import streamlit as st

from src.dashboard import ui
from src.database import repository as repo
from src.database.catalog import load_catalog

ui.setup_page("SQL Query Lab", "🧪", "Run the 20 required analysis queries (plus bonus analytics) live against the database")

catalog = load_catalog()
groups = list(dict.fromkeys(q.group for q in catalog))
group = st.sidebar.radio("Query group", groups)
subset = [q for q in catalog if q.group == group]
chosen = st.selectbox("Query", subset, format_func=lambda q: f"{q.query_id} - {q.title}")

values = {name: st.text_input(name, value=chosen.defaults.get(name, "")) for name in chosen.parameters}
st.code(chosen.sql, language="sql")

result = repo.run_catalog_query(chosen, values)
st.write(f"**{len(result):,}** rows")
ui.paged_table(result, f"lab_{chosen.query_id}", file_name=f"{chosen.query_id}.csv")
