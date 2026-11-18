"""Common helper functions."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
SAMPLE_DIR = PROJECT_ROOT / "data" / "sample"

RAW_FILES = {
    "competitions": "competitions.json",
    "complexes": "complexes.json",
    "rankings": "doubles_rankings.json",
}


def clean_text(value: Any, default: str | None = None) -> str | None:
    """Strip a value to text; return ``default`` when empty or missing."""
    if value is None:
        return default
    text = str(value).strip()
    return text if text else default


def safe_int(value: Any, default: int = 0) -> int:
    """Convert to int without raising (None, '', 'abc' -> default)."""
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def read_json(path: Path) -> dict[str, Any]:
    """Read a UTF-8 JSON file with a friendly error if it is missing."""
    if not path.exists():
        raise FileNotFoundError(
            f"{path} not found. Run `python main.py collect` (API) or "
            "`python main.py sample` (offline demo data) first."
        )
    with path.open(encoding="utf-8") as file:
        return json.load(file)
