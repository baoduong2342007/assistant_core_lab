"""Integration checks for environment wiring, auth, and core compatibility."""

import os

import httpx
import pytest
from fastapi.testclient import TestClient

from assistant_api.main import create_app
from assistant_api.weather import WeatherClient
from assistant_core.config import load_settings


def test_factory_loads_environment_and_owns_weather_client(monkeypatch, project_root):
    monkeypatch.setattr(os, "environ", {})
    for name, value in {
        "ASSISTANT_DATA_DIR": str(project_root / "data"),
        "API_ADMIN_KEY": "fake-env-admin",
        "WEATHER_URL": "https://weather.example.test/custom",
        "WEATHER_TIMEOUT_S": "1.5",
        "WEATHER_RETRIES": "0",
        "WEATHER_CACHE_TTL_S": "0",
        "CAMPUS_LAT": "21.03",
        "CAMPUS_LON": "105.85",
    }.items():
        monkeypatch.setenv(name, value)
    monkeypatch.setattr("assistant_api.main.load_settings", lambda: load_settings(env_file=None))
    requests = []
    weather_clients = []

    def handler(request):
        requests.append(request)
        return httpx.Response(
            200,
            json={
                "current": {
                    "time": "2026-11-01T12:00",
                    "temperature_2m": 30,
                    "wind_speed_10m": 5,
                    "weather_code": 0,
                }
            },
        )

    def build_weather(*args, **kwargs):
        weather = WeatherClient(*args, **kwargs, transport=httpx.MockTransport(handler))
        weather_clients.append(weather)
        return weather

    monkeypatch.setattr("assistant_api.main.WeatherClient", build_weather)
    with TestClient(create_app()) as client:
        assert client.get("/health").json() == {"status": "ok", "version": "1.0.0"}
        assert client.post("/v1/chat", json={"message": "hi"}).status_code == 200
        assert client.get("/v1/feedback", headers={"X-API-Key": "fake-env-admin"}).status_code == 200
        assert client.get("/v1/weather").status_code == 200
        assert client.get("/v1/weather").status_code == 200
        assert len(requests) == 2
        assert str(requests[0].url).startswith("https://weather.example.test/custom?")
        assert requests[0].url.params["latitude"] == "21.03"
        assert requests[0].url.params["longitude"] == "105.85"
        assert requests[0].extensions["timeout"]["read"] == 1.5
        assert weather_clients[0].retries == 0
    assert weather_clients[0]._client.is_closed


@pytest.mark.parametrize("key", [None, "", "wrong-admin"])
def test_invalid_admin_key_has_safe_401(sample_settings, service, key):
    settings = sample_settings.model_copy(update={"api_admin_key": "fake-private-admin"})
    with TestClient(create_app(settings, service)) as client:
        response = client.get("/v1/feedback", headers={"X-API-Key": key} if key is not None else {})
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "missing_or_invalid_api_key"
    assert "fake-private-admin" not in response.text


def test_admin_disabled_when_no_key_is_configured(sample_settings, service):
    with TestClient(create_app(sample_settings, service)) as client:
        assert client.get("/v1/feedback", headers={"X-API-Key": "change-me"}).status_code == 401


@pytest.mark.parametrize("message", ["   ", "\n\t", "x" * 2001, 123])
def test_invalid_chat_is_validation_error(sample_settings, service, message):
    with TestClient(create_app(sample_settings, service)) as client:
        response = client.post("/v1/chat", json={"message": message})
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "invalid_request"


def test_chat_reuses_core_response_and_unique_request_id(sample_settings, service):
    text = "H26-5.3"
    with TestClient(create_app(sample_settings, service)) as client:
        first = client.post("/v1/chat", json={"message": text, "session_id": "huy-lab04"}).json()
        second = client.post("/v1/chat", json={"message": text}).json()
    assert first["intent"] == "rule"
    assert any(source["id"] == text for source in first["sources"])
    assert first["request_id"] != second["request_id"]
