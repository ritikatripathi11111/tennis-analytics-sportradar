"""API client tests with a fake HTTP session (no network, no real key)."""
import pytest
import requests

from src.api.client import SportRadarAPIError, SportRadarClient


class FakeResponse:
    def __init__(self, status=200, payload=None, headers=None):
        self.status_code, self._payload, self.headers = status, payload, headers or {}
        self.text = str(payload)

    def json(self):
        return self._payload

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"HTTP {self.status_code}")


class FakeSession(requests.Session):
    def __init__(self, responses):
        super().__init__()
        self.responses = list(responses)

    def get(self, url, timeout=None, **kwargs):
        return self.responses.pop(0)


def make_client(*responses):
    return SportRadarClient(api_key="test-key", session=FakeSession(responses), max_retries=1)


def test_success_returns_json():
    client = make_client(FakeResponse(200, {"competitions": []}))
    assert client.get_json("competitions.json") == {"competitions": []}


def test_auth_failure_is_not_retried():
    client = make_client(FakeResponse(403, {}))
    with pytest.raises(SportRadarAPIError):
        client.get_json("competitions.json")


def test_rate_limit_retries_then_succeeds(monkeypatch):
    monkeypatch.setattr("time.sleep", lambda *_: None)
    client = make_client(FakeResponse(429, {}), FakeResponse(200, {"ok": True}))
    assert client.get_json("complexes.json") == {"ok": True}


def test_endpoint_must_be_json():
    with pytest.raises(ValueError):
        make_client().get_json("competitions")


def test_missing_key_raises(monkeypatch):
    monkeypatch.delenv("SPORTRADAR_API_KEY", raising=False)
    with pytest.raises(ValueError):
        SportRadarClient(api_key=None)
