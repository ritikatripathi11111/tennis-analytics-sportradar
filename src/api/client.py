from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
load_dotenv(PROJECT_ROOT / ".env")


class SportRadarAPIError(RuntimeError):
    """Raised when a SportRadar request or response cannot be processed."""


class SportRadarClient:
    """Small reusable HTTP client for SportRadar Tennis API v3."""

    def __init__(
        self,
        api_key: str | None = None,
        access_level: str | None = None,
        language: str | None = None,
        timeout: int = 30,
        max_retries: int = 2,
        session: requests.Session | None = None,
    ) -> None:
        self.api_key = api_key or os.getenv("SPORTRADAR_API_KEY")
        self.access_level = access_level or os.getenv(
            "SPORTRADAR_ACCESS_LEVEL", "trial"
        )
        self.language = language or os.getenv("SPORTRADAR_LANGUAGE", "en")
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = session or requests.Session()

        if not self.api_key:
            raise ValueError(
                "SPORTRADAR_API_KEY is missing. Add it to the project-root .env file."
            )
        if self.access_level not in {"trial", "production"}:
            raise ValueError("SPORTRADAR_ACCESS_LEVEL must be 'trial' or 'production'.")

        self.base_url = (
            "https://api.sportradar.com/tennis/"
            f"{self.access_level}/v3/{self.language}"
        )
        self.session.headers.update(
            {
                "accept": "application/json",
                "x-api-key": self.api_key,
                "user-agent": "tennis-analytics-sportradar/1.0",
            }
        )

    def get_json(self, endpoint: str) -> dict[str, Any]:
        """Request one JSON feed and return its unmodified JSON object."""
        endpoint = endpoint.lstrip("/")
        if not endpoint.endswith(".json"):
            raise ValueError("SportRadar endpoint must end with '.json'.")

        url = f"{self.base_url}/{endpoint}"
        for attempt in range(self.max_retries + 1):
            try:
                response = self.session.get(url, timeout=self.timeout)
            except requests.RequestException as exc:
                if attempt >= self.max_retries:
                    raise SportRadarAPIError(f"Network error requesting {endpoint}: {exc}") from exc
                time.sleep(2 ** attempt)
                continue

            if response.status_code == 429 or response.status_code >= 500:
                if attempt < self.max_retries:
                    retry_after = response.headers.get("Retry-After")
                    try:
                        delay = float(retry_after) if retry_after else 2 ** attempt
                    except ValueError:
                        delay = 2 ** attempt
                    time.sleep(min(delay, 30))
                    continue

            if response.status_code in (401, 403):
                raise SportRadarAPIError(
                    "SportRadar authentication/access failed "
                    f"(HTTP {response.status_code}). Check the API key, product entitlement "
                    "and trial/production access level."
                )
            if response.status_code == 429:
                raise SportRadarAPIError(
                    "SportRadar rate limit reached (HTTP 429). Try again later."
                )
            try:
                response.raise_for_status()
            except requests.HTTPError as exc:
                raise SportRadarAPIError(
                    f"SportRadar returned HTTP {response.status_code} for {endpoint}: "
                    f"{response.text[:500]}"
                ) from exc

            try:
                payload = response.json()
            except (ValueError, json.JSONDecodeError) as exc:
                raise SportRadarAPIError(
                    f"SportRadar returned a non-JSON response for {endpoint}."
                ) from exc

            if not isinstance(payload, dict):
                raise SportRadarAPIError(
                    f"Expected a JSON object from {endpoint}, received {type(payload).__name__}."
                )
            return payload

        raise SportRadarAPIError(f"Request failed for {endpoint}.")

    @staticmethod
    def save_json(payload: dict[str, Any], output_path: str | Path) -> Path:
        """Save a raw API response as UTF-8 JSON, replacing the file atomically."""
        destination = Path(output_path)
        if not destination.is_absolute():
            destination = PROJECT_ROOT / destination
        destination.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = destination.with_suffix(destination.suffix + ".tmp")
        try:
            with temporary_path.open("w", encoding="utf-8") as file:
                json.dump(payload, file, ensure_ascii=False, indent=2)
                file.write("\n")
            temporary_path.replace(destination)
        except OSError as exc:
            temporary_path.unlink(missing_ok=True)
            raise SportRadarAPIError(f"Could not save JSON to {destination}: {exc}") from exc
        return destination

    def fetch_and_save(self, endpoint: str, filename: str) -> Path:
        """Fetch a feed and save its original JSON response under data/raw/."""
        if Path(filename).name != filename or not filename.endswith(".json"):
            raise ValueError("filename must be a simple .json filename, not a path.")
        payload = self.get_json(endpoint)
        destination = self.save_json(payload, RAW_DATA_DIR / filename)
        print(f"Saved {endpoint} -> {destination.relative_to(PROJECT_ROOT)}")
        return destination
