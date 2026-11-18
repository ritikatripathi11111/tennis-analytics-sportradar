"""Centralised SQLAlchemy engine creation and schema initialisation."""
from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL, Engine
from sqlalchemy.exc import SQLAlchemyError

from src.utils.helpers import PROJECT_ROOT
from src.utils.logger import get_logger

load_dotenv(PROJECT_ROOT / ".env")
log = get_logger(__name__)

SCHEMA_DIR = Path(__file__).resolve().parent


class DatabaseError(RuntimeError):
    """Raised when the database cannot be reached or initialised."""


def _engine_name() -> str:
    return os.getenv("DB_ENGINE", "mysql").strip().lower()


def _mysql_url(with_database: bool = True) -> URL:
    return URL.create(
        "mysql+pymysql",
        username=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "3306")),
        database=os.getenv("DB_NAME", "tennis_analytics") if with_database else None,
        query={"charset": "utf8mb4"},
    )


def _ensure_mysql_database() -> None:
    """Create the MySQL database if it does not exist yet."""
    name = os.getenv("DB_NAME", "tennis_analytics")
    if not name.replace("_", "").isalnum():
        raise DatabaseError("DB_NAME may only contain letters, digits and underscores.")
    bootstrap = create_engine(_mysql_url(with_database=False))
    try:
        with bootstrap.begin() as conn:
            conn.execute(
                text(f"CREATE DATABASE IF NOT EXISTS `{name}` "
                     "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            )
    finally:
        bootstrap.dispose()


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    """Return a cached engine for MySQL (default) or SQLite (demo)."""
    try:
        if _engine_name() == "sqlite":
            path = Path(os.getenv("SQLITE_PATH", "data/processed/tennis.db"))
            if not path.is_absolute():
                path = PROJECT_ROOT / path
            path.parent.mkdir(parents=True, exist_ok=True)
            return create_engine(f"sqlite:///{path.as_posix()}")
        _ensure_mysql_database()
        return create_engine(_mysql_url(), pool_pre_ping=True, pool_recycle=1800)
    except SQLAlchemyError as exc:
        raise DatabaseError(
            f"Could not connect to the database: {exc}. "
            "Check DB_* values in .env (or set DB_ENGINE=sqlite)."
        ) from exc


def _split_statements(script: str) -> list[str]:
    """Split a SQL script on ';' after removing '--' comment lines."""
    lines = [ln for ln in script.splitlines() if not ln.strip().startswith("--")]
    return [stmt.strip() for stmt in "\n".join(lines).split(";") if stmt.strip()]


def init_schema(engine: Engine | None = None) -> None:
    """Create all tables and the latest-rankings view (idempotent)."""
    engine = engine or get_engine()
    script_name = "schema_sqlite.sql" if engine.dialect.name == "sqlite" else "schema.sql"
    statements = _split_statements((SCHEMA_DIR / script_name).read_text(encoding="utf-8"))
    try:
        with engine.begin() as conn:
            for statement in statements:
                conn.execute(text(statement))
    except SQLAlchemyError as exc:
        raise DatabaseError(f"Schema initialisation failed: {exc}") from exc
    log.info("Schema ready (%s, %d statements).", engine.dialect.name, len(statements))
