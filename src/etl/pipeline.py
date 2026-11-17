"""End-to-end ETL: raw/sample JSON -> transform -> validate -> SQL."""
from __future__ import annotations

from pathlib import Path

from src.database.connection import get_engine, init_schema
from src.etl.loader import load_all
from src.etl.transform import parse_competitions, parse_complexes, parse_rankings
from src.etl.validate import validate_frames
from src.utils.helpers import RAW_DIR, RAW_FILES, SAMPLE_DIR, read_json
from src.utils.logger import get_logger

log = get_logger(__name__)


def run_etl(source: str = "api") -> dict[str, int]:
    """Run the ETL for ``source`` in {'api', 'sample'}; return loaded row counts."""
    if source not in {"api", "sample"}:
        raise ValueError("source must be 'api' or 'sample'")
    folder: Path = RAW_DIR if source == "api" else SAMPLE_DIR
    log.info("ETL started (source=%s, folder=%s)", source, folder)

    frames = {}
    frames.update(parse_competitions(read_json(folder / RAW_FILES["competitions"])))
    frames.update(parse_complexes(read_json(folder / RAW_FILES["complexes"])))
    frames.update(parse_rankings(read_json(folder / RAW_FILES["rankings"])))

    frames, issues = validate_frames(frames)
    engine = get_engine()
    init_schema(engine)
    load_all(engine, frames, data_source=source)

    counts = {table: len(df) for table, df in frames.items()}
    log.info("ETL finished: %s (%d data-quality notes)", counts, len(issues))
    return counts
