from pathlib import Path

from src.api.client import SportRadarClient


ENDPOINT = "double_competitors_rankings.json"
OUTPUT_FILE = "doubles_rankings.json"


def collect_doubles_rankings(client: SportRadarClient | None = None) -> Path:
    """Fetch the doubles competitor rankings feed and save raw JSON."""
    api = client or SportRadarClient()
    return api.fetch_and_save(ENDPOINT, OUTPUT_FILE)