# Game Analytics: Unlocking Tennis Data with SportRadar API

End-to-end data analytics project: **SportRadar API -> Python ETL -> SQL database -> interactive Streamlit dashboard**.

## What it demonstrates
| Skill | Evidence |
|---|---|
| API integration | Authenticated client with retries, rate-limit handling, atomic raw-JSON storage (`src/api/`) |
| Data engineering | Nested JSON flattened, validated and loaded transactionally; idempotent weekly snapshots (`src/etl/`) |
| SQL | 6 normalised tables + view, indexes, **20 required queries + 4 bonus analytics** (`src/database/`) |
| Analytics and BI | 7 dashboard pages: KPIs, world maps, sunburst, treemap, bubble charts, drill-downs, auto-generated insights |
| Engineering quality | Modular code, docstrings, type hints, logging, unit tests, `.env` secrets, offline demo mode |

## Dashboard pages
Overview | Competitions Explorer (hierarchy drill-down) | Venues and Complexes | Doubles Player Rankings (search, filters, competitor detail) | Country-wise Analysis | Smart Insights | SQL Query Lab (runs all 24 queries live)

## Quick start (VS Code, Windows PowerShell)
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env        # then edit .env (key + DB password)
```
**Option A - offline demo (no API, no MySQL):** set `DB_ENGINE=sqlite` in `.env`, then
```powershell
python main.py sample          # synthetic data -> SQLite
streamlit run src/dashboard/app.py
```
**Option B - real data (MySQL):**
```powershell
python main.py collect         # SportRadar -> data/raw/*.json (3 API calls)
python main.py load            # JSON -> MySQL (creates DB + tables)
streamlit run src/dashboard/app.py
```
`python main.py all` runs collect + load. Run `pytest` to execute the tests.

## Security
Never commit `.env` (already in `.gitignore`). Keep the API key only in `.env`. If a key was ever pasted into a chat, screenshot or repository, regenerate it in the SportRadar console.

## Notes
- Trial keys are rate limited (about 1 request/second); the collector pauses between calls.
- Maps use the ISO-3 `country_code` from the API; unusual codes simply will not shade.
- Re-run `collect` + `load` weekly: each week is stored as a new snapshot, enabling rank-history charts.

See `docs/` for architecture, database design and the full SQL documentation.
