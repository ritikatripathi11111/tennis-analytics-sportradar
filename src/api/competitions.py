from pathlib import Path

from src.api.client import SportRadarClient


ENDPOINT = "competitions.json"
OUTPUT_FILE = "competitions.json"


def collect_competitions(client: SportRadarClient | None = None) -> Path:
    """Fetch the competitions feed and save the raw JSON response."""
    api = client or SportRadarClient()
    return api.fetch_and_save(ENDPOINT, OUTPUT_FILE)