# Architecture

```mermaid
flowchart LR
    A[SportRadar Tennis API v3] -->|src/api| B[data/raw/*.json]
    S[scripts/generate_sample_data.py] -->|offline demo| C[data/sample/*.json]
    B --> D[src/etl: transform -> validate -> load]
    C --> D
    D --> E[(MySQL / SQLite)]
    E -->|src/database/repository.py| F[Streamlit dashboard]
    E --> G[SQL Query Lab: 20 required + 4 bonus queries]
```

| Layer | Files | Responsibility |
|---|---|---|
| Extract | `src/api/` | Authenticated GET, retries on 429/5xx, atomic JSON save |
| Transform | `src/etl/transform.py` | Nested JSON -> flat DataFrames |
| Validate | `src/etl/validate.py` | Keys, duplicates, lengths, referential integrity |
| Load | `src/etl/loader.py` | One transaction; full refresh for dimensions, snapshot upsert for rankings |
| Serve | `src/database/repository.py` | Parameterised SQL (filters run in the database) |
| Present | `src/dashboard/` | 7 Streamlit pages, Plotly charts, rule-based insights |
