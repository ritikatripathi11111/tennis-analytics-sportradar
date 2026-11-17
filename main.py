"""Command-line entry point.

python main.py collect   # call SportRadar and save raw JSON in data/raw/
python main.py load      # ETL data/raw/*.json -> SQL database
python main.py all       # collect + load
python main.py sample    # offline demo: synthetic JSON -> SQL database
"""
from __future__ import annotations

import argparse
import time

from src.api.client import SportRadarAPIError
from src.api.competitions import collect_competitions
from src.api.complexes import collect_complexes
from src.api.rankings import collect_doubles_rankings
from src.database.connection import DatabaseError
from src.etl.pipeline import run_etl

# Trial keys allow ~1 request per second, so pause between feeds.
API_PAUSE_SECONDS = 1.5


def collect() -> int:
    """Run each feed independently and return a non-zero code on failure."""
    tasks = [
        ("Competitions", collect_competitions),
        ("Complexes and venues", collect_complexes),
        ("Doubles competitor rankings", collect_doubles_rankings),
    ]
    failures: list[str] = []

    print("Starting SportRadar Tennis data collection...\n")
    for index, (name, collector) in enumerate(tasks):
        if index:
            time.sleep(API_PAUSE_SECONDS)
        print(f"[{name}]")
        try:
            path = collector()
            print(f"SUCCESS: {path}\n")
        except (SportRadarAPIError, ValueError) as exc:
            failures.append(name)
            print(f"FAILED: {exc}\n")

    if failures:
        print("Collection finished with failures: " + ", ".join(failures))
        return 1
    print("All three raw JSON feeds were collected successfully.")
    return 0


def load(source: str) -> int:
    """Run the ETL pipeline and report errors without a stack trace."""
    try:
        counts = run_etl(source)
    except (FileNotFoundError, DatabaseError, ValueError) as exc:
        print(f"ETL FAILED: {exc}")
        return 1
    print("Loaded rows:", counts)
    print("Next: streamlit run src/dashboard/app.py")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("command", nargs="?", default="collect",
                        choices=["collect", "load", "all", "sample"])
    command = parser.parse_args().command

    if command == "collect":
        return collect()
    if command == "load":
        return load("api")
    if command == "all":
        return collect() or load("api")
    from scripts.generate_sample_data import main as generate_sample  # noqa: PLC0415
    generate_sample()
    return load("sample")


if __name__ == "__main__":
    raise SystemExit(main())
