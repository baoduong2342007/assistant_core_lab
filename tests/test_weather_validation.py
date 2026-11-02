"""Lab04 regressions for malformed upstream weather responses."""

import httpx
import pytest
from fastapi.testclient import TestClient

from assistant_api.main import create_app
from assistant_api.weather import WeatherClient

INVALID = [
    [],
    None,
    {"current": None},
    {"current": []},
    {"current": {}},
    {"current": {"time": "now", "temperature_2m": 30, "wind_speed_10m": 5, "weather_code": []}},
    {"current": {"time": "now", "temperature_2m": "NaN", "wind_speed_10m": 5, "weather_code": 3}},
]
VALID = {"current": {"time": "2026-11-02T10:00", "temperature_2m": 30, "wind_speed_10m": 5, "weather_code": 3}}


@pytest.mark.parametrize("payload", INVALID)
@pytest.mark.parametrize("cached", [False, True])
def test_invalid_upstream_uses_error_or_stale_cache(sample_settings, service, monkeypatch, payload, cached):
    calls = []

    def handler(request):
        calls.append(request)
        return httpx.Response(200, json=VALID if cached and len(calls) == 1 else payload)

    monkeypatch.setattr("assistant_api.weather.time.sleep", lambda seconds: None)
    weather = WeatherClient(
        "https://example.test", 10, 106, cache_ttl_s=0, retries=1, transport=httpx.MockTransport(handler)
    )
    if cached:
        assert not weather.current().stale
    with TestClient(create_app(sample_settings, service, weather)) as client:
        response = client.get("/v1/weather")
    if cached:
        assert response.status_code == 200
        assert response.json()["stale"] is True
        assert response.json()["temperature_c"] == 30
    else:
        assert response.status_code == 503
        assert response.json()["error"]["code"] == "weather_service_unavailable"
    assert len(calls) == (3 if cached else 2)
