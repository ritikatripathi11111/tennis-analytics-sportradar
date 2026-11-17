"""Parse queries.sql into a catalog of named, documented queries (stdlib only)."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

QUERIES_FILE = Path(__file__).resolve().parent / "queries.sql"
_META = re.compile(r"^--\s*@(\w+):\s*(.*)$")
_PARAM = re.compile(r"(?<!:):([A-Za-z_]\w*)")


@dataclass(frozen=True)
class CatalogQuery:
    """One documented SQL query."""

    query_id: str
    group: str
    title: str
    sql: str
    defaults: dict[str, str] = field(default_factory=dict)

    @property
    def parameters(self) -> list[str]:
        """Named bind parameters used in the SQL, in order of appearance."""
        return list(dict.fromkeys(_PARAM.findall(self.sql)))


def load_catalog(path: Path = QUERIES_FILE) -> list[CatalogQuery]:
    """Read every '-- @id' block from the SQL file."""
    queries: list[CatalogQuery] = []
    meta: dict[str, str] = {}
    body: list[str] = []

    def flush() -> None:
        if meta.get("id") and body:
            sql = "\n".join(body).strip().rstrip(";").strip()
            defaults = dict(
                part.split("=", 1) for part in meta.get("params", "").split(";") if "=" in part
            )
            queries.append(
                CatalogQuery(meta["id"], meta.get("group", ""), meta.get("title", ""), sql, defaults)
            )

    for line in path.read_text(encoding="utf-8").splitlines():
        match = _META.match(line.strip())
        if match:
            key, value = match.groups()
            if key == "id":
                flush()
                meta, body = {}, []
            meta[key] = value.strip()
        elif line.strip().startswith("--"):
            continue  # ordinary comment
        elif line.strip() or body:
            body.append(line)
    flush()
    return queries
