"""Lab04 API configuration tests; Week 3 tests remain unchanged."""

import os

import pytest
from pydantic import ValidationError

from assistant_core.config import Settings, load_settings
from assistant_core.errors import ConfigError


@pytest.fixture(autouse=True)
def isolated_environment(monkeypatch):
    """Use a private environment copy so dotenv cannot leak between tests."""
    monkeypatch.setattr(os, "environ", os.environ.copy())
    for name in (
        "ASSISTANT_DATA_DIR",
        "LLM_PROVIDER",
        "LLM_API_KEY",
        "CREDIT_RATE_VND",
        "RETAKE_MULTIPLIER",
        "MAX_CREDITS",
        "LOG_LEVEL",
        "API_ADMIN_KEY",
        "WEATHER_URL",
        "WEATHER_TIMEOUT_S",
        "WEATHER_RETRIES",
        "WEATHER_CACHE_TTL_S",
        "CAMPUS_LAT",
        "CAMPUS_LON",
        "RATE_LIMIT_PER_MIN",
    ):
        monkeypatch.delenv(name, raising=False)


def test_api_settings_defaults():
    settings = load_settings(env_file=None)
    assert settings.api_admin_key is None
    assert settings.weather_url == "https://api.open-meteo.com/v1/forecast"
    assert settings.weather_timeout_s == 3
    assert settings.weather_retries == 1
    assert settings.weather_cache_ttl_s == 600
    assert (settings.campus_lat, settings.campus_lon) == (10.7626, 106.6822)
    assert settings.rate_limit_per_min == 30


def test_api_environment_and_dotenv_precedence(monkeypatch, tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text(
        "API_ADMIN_KEY=dotenv-demo-key\nWEATHER_URL=https://weather.example.test/forecast\n"
        "WEATHER_TIMEOUT_S=1.25\nWEATHER_RETRIES=2\nWEATHER_CACHE_TTL_S=60\n"
        "CAMPUS_LAT=21.03\nCAMPUS_LON=105.85\nRATE_LIMIT_PER_MIN=12\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("API_ADMIN_KEY", "environment-demo-key")
    monkeypatch.setenv("WEATHER_TIMEOUT_S", "2.5")
    settings = load_settings(env_file)
    assert settings.api_admin_key == "environment-demo-key"
    assert settings.weather_timeout_s == 2.5
    assert settings.weather_url == "https://weather.example.test/forecast"
    assert settings.weather_retries == 2
    assert settings.weather_cache_ttl_s == 60
    assert (settings.campus_lat, settings.campus_lon) == (21.03, 105.85)
    assert settings.rate_limit_per_min == 12


@pytest.mark.parametrize("value", ["", None])
def test_missing_or_empty_admin_key_disables_admin(monkeypatch, value):
    if value is not None:
        monkeypatch.setenv("API_ADMIN_KEY", value)
    assert load_settings(env_file=None).api_admin_key is None


@pytest.mark.parametrize(
    ("name", "value", "field"),
    [
        ("API_ADMIN_KEY", "   ", "api_admin_key"),
        ("WEATHER_URL", "not-a-url", "weather_url"),
        ("WEATHER_URL", "ftp://weather.example.test/forecast", "weather_url"),
        ("WEATHER_URL", "https://user:password@weather.example.test/", "weather_url"),
        ("WEATHER_TIMEOUT_S", "0", "weather_timeout_s"),
        ("WEATHER_TIMEOUT_S", "-1", "weather_timeout_s"),
        ("WEATHER_TIMEOUT_S", "nan", "weather_timeout_s"),
        ("WEATHER_TIMEOUT_S", "inf", "weather_timeout_s"),
        ("WEATHER_TIMEOUT_S", "abc", "weather_timeout_s"),
        ("WEATHER_RETRIES", "-1", "weather_retries"),
        ("WEATHER_RETRIES", "1.5", "weather_retries"),
        ("WEATHER_CACHE_TTL_S", "-1", "weather_cache_ttl_s"),
        ("WEATHER_CACHE_TTL_S", "nan", "weather_cache_ttl_s"),
        ("CAMPUS_LAT", "90.1", "campus_lat"),
        ("CAMPUS_LAT", "-90.1", "campus_lat"),
        ("CAMPUS_LAT", "nan", "campus_lat"),
        ("CAMPUS_LON", "180.1", "campus_lon"),
        ("CAMPUS_LON", "-180.1", "campus_lon"),
        ("CAMPUS_LON", "inf", "campus_lon"),
        ("RATE_LIMIT_PER_MIN", "0", "rate_limit_per_min"),
        ("RATE_LIMIT_PER_MIN", "2.5", "rate_limit_per_min"),
    ],
)
def test_invalid_api_environment_fails_safely(monkeypatch, name, value, field):
    monkeypatch.setenv("API_ADMIN_KEY", "fake-secret-do-not-log")
    monkeypatch.setenv(name, value)
    with pytest.raises(ConfigError, match=field) as error:
        load_settings(env_file=None)
    assert "fake-secret-do-not-log" not in str(error.value)
    assert "password" not in str(error.value)


def test_api_secret_excluded_and_validation_hides_input():
    secret = "fake-admin-do-not-log"
    settings = Settings(api_admin_key=secret)
    assert secret not in repr(settings)
    assert "api_admin_key" not in settings.model_dump()
    assert secret not in settings.model_dump_json()
    with pytest.raises(ValidationError) as error:
        Settings(weather_timeout_s="fake-sensitive-value", api_admin_key=secret)
    assert "fake-sensitive-value" not in str(error.value)
    assert secret not in str(error.value)


def test_api_numeric_boundaries_allow_disabling_cache_and_retry():
    settings = Settings(campus_lat=-90, campus_lon=180, weather_retries=0, weather_cache_ttl_s=0)
    assert settings.weather_retries == 0
    assert settings.weather_cache_ttl_s == 0
