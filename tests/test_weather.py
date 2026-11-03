"""Huy's weather regression: real client, fake HTTP, deterministic cache clock."""

from types import SimpleNamespace

import httpx
import pytest
from fastapi.testclient import TestClient

from assistant_api.main import create_app
from assistant_api.weather import ExternalServiceError, WeatherClient

OK_JSON = {"current": {"time": "2026-11-01T12:00", "temperature_2m": 31.2, "weather_code": 3, "wind_speed_10m": 8.5}}


@pytest.fixture
def clock(monkeypatch):
    clock = SimpleNamespace(now=1000.0, sleeps=[])
    monkeypatch.setattr(
        "assistant_api.weather.time", SimpleNamespace(monotonic=lambda: clock.now, sleep=clock.sleeps.append)
    )
    return clock


@pytest.fixture
def weather_factory(clock):
    clients = []

    def make(handler, **kwargs):
        client = WeatherClient(
            "https://weather.example.test/forecast", 10.76, 106.68, transport=httpx.MockTransport(handler), **kwargs
        )
        clients.append(client)
        return client

    yield make
    for client in clients:
        client.close()


def test_weather_sends_coordinates_timeout_and_caches(weather_factory, clock):
    requests = []

    def handler(request):
        requests.append(request)
        return httpx.Response(200, json=OK_JSON)

    weather = weather_factory(handler, timeout_s=1.25)
    first = weather.current()
    clock.now += 599
    assert weather.current() == first
    assert len(requests) == 1
    assert requests[0].url.params["latitude"] == "10.76"
    assert requests[0].url.params["longitude"] == "106.68"
    assert requests[0].url.params["current"] == "temperature_2m,weather_code,wind_speed_10m"
    assert all(value == 1.25 for value in requests[0].extensions["timeout"].values())
    assert first.model_dump() == {
        "temperature_c": 31.2,
        "wind_kmh": 8.5,
        "description": "overcast",
        "observed_at": "2026-11-01T12:00",
        "stale": False,
    }
    assert clock.sleeps == []


@pytest.mark.parametrize(
    "failure",
    [
        "timeout",
        "connect",
        429,
        500,
        "invalid-json",
        {},
        [],
        {"current": None},
        {"current": []},
        {"current": {"temperature_2m": "invalid"}},
    ],
)
def test_upstream_failures_retry_once_then_api_503(failure, weather_factory, clock, sample_settings, service, caplog):
    calls = []

    def handler(request):
        calls.append(request)
        if failure == "timeout":
            raise httpx.ReadTimeout("fake-upstream-secret", request=request)
        if failure == "connect":
            raise httpx.ConnectError("fake-upstream-secret", request=request)
        if isinstance(failure, int):
            return httpx.Response(failure, text="fake-upstream-secret")
        if failure == "invalid-json":
            return httpx.Response(200, text="fake-upstream-secret")
        return httpx.Response(200, json=failure)

    weather = weather_factory(handler)
    with TestClient(create_app(sample_settings, service, weather)) as client:
        response = client.get("/v1/weather")
    assert response.status_code == 503
    assert response.json() == {
        "error": {"code": "weather_service_unavailable", "message": "Weather service unavailable"}
    }
    assert len(calls) == 2
    assert clock.sleeps == [0.2]
    assert "fake-upstream-secret" not in response.text
    assert "fake-upstream-secret" not in caplog.text


def test_transient_timeout_recovers_on_retry(weather_factory, clock):
    calls = []

    def handler(request):
        calls.append(request)
        if len(calls) == 1:
            raise httpx.ConnectTimeout("simulated timeout", request=request)
        return httpx.Response(200, json=OK_JSON)

    weather = weather_factory(handler)
    assert weather.current().stale is False
    assert len(calls) == 2
    assert clock.sleeps == [0.2]


def test_expired_cache_serves_stale_then_refresh_recovers(weather_factory, clock, sample_settings, service):
    calls = []

    def handler(request):
        calls.append(request)
        if len(calls) in (2, 3):
            return httpx.Response(500)
        return httpx.Response(200, json=OK_JSON)

    weather = weather_factory(handler)
    with TestClient(create_app(sample_settings, service, weather)) as client:
        fresh = client.get("/v1/weather")
        assert fresh.status_code == 200 and fresh.json()["stale"] is False
        clock.now += 600  # At TTL boundary the client must attempt a refresh.
        stale = client.get("/v1/weather")
        assert stale.status_code == 200 and stale.json()["stale"] is True
        assert stale.json()["temperature_c"] == fresh.json()["temperature_c"]
        assert len(calls) == 3
        recovered = client.get("/v1/weather")
        assert recovered.status_code == 200 and recovered.json()["stale"] is False
        assert len(calls) == 4
        assert client.get("/v1/weather").json()["stale"] is False
        assert len(calls) == 4


def test_zero_retries_means_one_attempt_no_sleep(weather_factory, clock):
    requests = []

    def handler(request):
        requests.append(request)
        return httpx.Response(500)

    weather = weather_factory(handler, retries=0)
    with pytest.raises(ExternalServiceError):
        weather.current()
    assert len(requests) == 1
    assert clock.sleeps == []


def test_zero_cache_ttl_refreshes_each_call(weather_factory):
    requests = []

    def handler(request):
        requests.append(request)
        return httpx.Response(200, json=OK_JSON)

    weather = weather_factory(handler, cache_ttl_s=0)
    weather.current()
    weather.current()
    assert len(requests) == 2
