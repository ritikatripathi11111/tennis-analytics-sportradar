from pathlib import Path

from src.api.client import SportRadarClient


ENDPOINT = "complexes.json"
OUTPUT_FILE = "complexes.json"


def collect_complexes(client: SportRadarClient | None = None) -> Path:
    """Fetch the complexes feed (including venues) and save raw JSON."""
    api = client or SportRadarClient()
    return api.fetch_and_save(ENDPOINT, OUTPUT_FILE)