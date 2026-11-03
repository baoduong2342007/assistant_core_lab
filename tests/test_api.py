import httpx
import pytest
from fastapi.testclient import TestClient

from assistant_api.main import create_app
from assistant_api.weather import WeatherClient

OK_JSON = {"current": {"time": "2026-10-05T09:00", "temperature_2m": 31.2, "weather_code": 3, "wind_speed_10m": 8.5}}


def weather_with(handler) -> WeatherClient:
    transport = httpx.MockTransport(handler)
    return WeatherClient("https://example.test/forecast", 10.76, 106.68, retries=1, transport=transport)


@pytest.fixture
def client(sample_settings, service):
    settings = sample_settings
    settings = settings.model_copy(update={"api_admin_key": "secret-admin", "rate_limit_per_min": 5})
    app = create_app(settings, service, weather_with(lambda req: httpx.Response(200, json=OK_JSON)))
    return TestClient(app)


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200 and r.json()["status"] == "ok"


def test_chat_fee(client):
    r = client.post("/v1/chat", json={"message": "tuition for 18 credits and 2 retake"})
    assert r.status_code == 200
    body = r.json()
    assert body["intent"] == "fee" and "9,450,000" in body["answer"] and body["request_id"]


def test_chat_validation_error(client):
    r = client.post("/v1/chat", json={"message": ""})
    assert r.status_code == 422 and r.json()["error"]["code"] == "invalid_request"


def test_rate_limit(client):
    codes = [client.post("/v1/chat", json={"message": "hi"}).status_code for _ in range(6)]
    assert codes == [200, 200, 200, 200, 200, 429]
    assert client.post("/v1/chat", json={"message": "hi"}).json()["error"]["code"] == "too_many_requests"


def test_feedback_roundtrip(client):
    r = client.post("/v1/feedback", json={"request_id": "abc123", "rating": 1})
    assert r.status_code == 201 and r.json()["id"] == 1
    assert client.get("/v1/feedback").status_code == 401
    listed = client.get("/v1/feedback", headers={"X-API-Key": "secret-admin"})
    assert listed.status_code == 200 and len(listed.json()) == 1


def test_feedback_rating_out_of_range(client):
    assert client.post("/v1/feedback", json={"request_id": "x", "rating": 5}).status_code == 422


def test_weather_ok(client):
    r = client.get("/v1/weather")
    assert r.status_code == 200 and r.json()["description"] == "overcast"


def test_weather_down_returns_503(sample_settings, service):
    settings = sample_settings

    def boom(req):
        raise httpx.ConnectTimeout("timeout", request=req)

    app = create_app(settings, service, weather_with(boom))
    r = TestClient(app).get("/v1/weather")
    assert r.status_code == 503 and r.json()["error"]["code"] == "weather_service_unavailable"


def test_weather_stale_cache_when_upstream_fails():
    calls = {"n": 0}

    def flaky(req):
        calls["n"] += 1
        if calls["n"] == 1:
            return httpx.Response(200, json=OK_JSON)
        return httpx.Response(500)

    w = weather_with(flaky)
    w.cache_ttl_s = 0  # force a refresh on the second call
    assert not w.current().stale
    assert w.current().stale


def test_offices_status(client):
    assert client.get("/v1/offices").status_code == 200


def test_offices_sorted_and_include_library(client):
    offices = client.get("/v1/offices").json()
    assert any(office["name"] == "Library" for office in offices)
    assert [office["name"] for office in offices] == sorted(office["name"] for office in offices)


def test_chat_blank_message(client):
    r = client.post("/v1/chat", json={"message": "   "})
    assert r.status_code == 422 and r.json()["error"]["code"] == "invalid_request"


def test_api_settings_environment(monkeypatch):
    from assistant_core.config import load_settings

    monkeypatch.setenv("API_ADMIN_KEY", "private-test-key")
    monkeypatch.setenv("WEATHER_TIMEOUT_S", "2.5")
    settings = load_settings(env_file=None)
    assert settings.api_admin_key == "private-test-key"
    assert settings.weather_timeout_s == 2.5
    assert "private-test-key" not in repr(settings)


def test_rate_limit_clients_and_expiry(monkeypatch):
    from assistant_api.ratelimit import RateLimiter

    now = [100.0]
    monkeypatch.setattr("assistant_api.ratelimit.time.monotonic", lambda: now[0])
    limiter = RateLimiter(1)
    assert limiter.allow("first")
    assert not limiter.allow("first")
    assert limiter.allow("second")
    now[0] += 61
    assert limiter.allow("first")


@pytest.fixture
def settings(sample_settings):
    """Keep API-only fixture names local; preserve the shared core fixtures."""
    return sample_settings


def test_offices_include_library_and_sorted_core_data(client, service):
    offices = client.get("/v1/offices").json()
    assert any(office["name"] == "Library" for office in offices)
    assert offices == [office.__dict__ for office in service.offices.all()]
    assert [office["name"] for office in offices] == ["IT Helpdesk", "Library", "Student Affairs", "Training Office"]


def test_feedback_rating_valid_boundaries(client):
    r_down = client.post("/v1/feedback", json={"request_id": "req-down", "rating": -1})
    assert r_down.status_code == 201 and r_down.json()["rating"] == -1

    r_neutral = client.post("/v1/feedback", json={"request_id": "req-neutral", "rating": 0})
    assert r_neutral.status_code == 201 and r_neutral.json()["rating"] == 0


def test_feedback_comment_length_limit(client):
    long_comment = "a" * 501
    r = client.post("/v1/feedback", json={"request_id": "req-comment", "rating": 1, "comment": long_comment})
    assert r.status_code == 422 and r.json()["error"]["code"] == "invalid_request"


@pytest.mark.parametrize(
    "bad_payload",
    [
        [],
        {"current": None},
        {"current": []},
        {"current": {"time": "2026-11-02T10:00", "temperature_2m": "NaN", "wind_speed_10m": 5, "weather_code": 3}},
        {"current": {"time": "2026-11-02T10:00", "temperature_2m": "Infinity", "wind_speed_10m": 5, "weather_code": 3}},
        {"current": {"time": "2026-11-02T10:00", "temperature_2m": "-inf", "wind_speed_10m": 5, "weather_code": 3}},
        {"current": {"time": "2026-11-02T10:00", "temperature_2m": 25.0, "wind_speed_10m": "NaN", "weather_code": 3}},
    ],
)
def test_weather_upstream_malformed_or_non_finite_returns_503_without_cache(sample_settings, service, bad_payload):
    settings = sample_settings
    app = create_app(settings, service, weather_with(lambda req: httpx.Response(200, json=bad_payload)))
    r = TestClient(app).get("/v1/weather")
    assert r.status_code == 503 and r.json()["error"]["code"] == "weather_service_unavailable"


def test_weather_upstream_non_finite_returns_stale_cache_when_cached(sample_settings, service):
    settings = sample_settings
    calls = {"n": 0}
    nan_payload = {
        "current": {"time": "2026-11-02T10:00", "temperature_2m": "NaN", "wind_speed_10m": 5, "weather_code": 3}
    }

    def handler(req):
        calls["n"] += 1
        if calls["n"] == 1:
            return httpx.Response(200, json=OK_JSON)
        return httpx.Response(200, json=nan_payload)

    weather = weather_with(handler)
    weather.cache_ttl_s = 0  # force a refresh on the second call
    app = create_app(settings, service, weather)
    client = TestClient(app)

    # First call: healthy, caches valid finite values
    r1 = client.get("/v1/weather")
    assert r1.status_code == 200 and not r1.json()["stale"]
    assert r1.json()["temperature_c"] == 31.2

    # Second call: upstream returns NaN, client rejects NaN before caching and serves stale cache
    r2 = client.get("/v1/weather")
    assert r2.status_code == 200
    body = r2.json()
    assert body["stale"] is True
    assert body["temperature_c"] == 31.2


@pytest.mark.parametrize("bad_payload", [[], {"current": None}, {"current": []}])
def test_weather_malformed_json_returns_503(settings, service, bad_payload):
    app = create_app(settings, service, weather_with(lambda req: httpx.Response(200, json=bad_payload)))
    r = TestClient(app).get("/v1/weather")
    assert r.status_code == 503 and r.json()["error"]["code"] == "weather_service_unavailable"


def test_offices_ok(client):
    r = client.get("/v1/offices")
    assert r.status_code == 200


def test_offices_contains_library(client):
    r = client.get("/v1/offices")
    assert r.status_code == 200
    offices = r.json()
    assert any(o.get("name") == "Library" for o in offices)
    names = [o["name"] for o in offices]
    assert names == sorted(names)
