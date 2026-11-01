"""Unit tests for configuration management."""

import os
from pathlib import Path

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


def test_settings_defaults():
    s = Settings()
    assert s.data_dir == Path("data")
    assert s.llm_provider == "stub"
    assert s.llm_api_key is None
    assert s.credit_rate_vnd == 450_000
    assert s.retake_multiplier == 1.5
    assert s.max_credits == 30
    assert s.log_level == "INFO"


def test_settings_repr_masks_api_key():
    s = Settings(llm_api_key="secret-key-12345")
    assert "secret-key-12345" not in repr(s)


def test_settings_validation():
    with pytest.raises(ValidationError):
        Settings(credit_rate_vnd=-100)
    with pytest.raises(ValidationError):
        Settings(retake_multiplier=0)
    with pytest.raises(ValidationError):
        Settings(max_credits=-5)
    with pytest.raises(ValidationError):
        Settings(log_level="NOT_A_LEVEL")


@pytest.mark.parametrize("key", ["", "fake-key-do-not-log"])
def test_load_settings_rejects_unsupported_provider_even_with_key(monkeypatch, key):
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("LLM_API_KEY", key)
    with pytest.raises(ConfigError, match="llm_provider"):
        load_settings(env_file=None)


def test_load_settings_from_env(monkeypatch):
    monkeypatch.setenv("CREDIT_RATE_VND", "500000")
    monkeypatch.setenv("MAX_CREDITS", "25")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    s = load_settings(env_file=None)
    assert s.credit_rate_vnd == 500_000
    assert s.max_credits == 25
    assert s.log_level == "DEBUG"


def test_load_settings_invalid_env_types(monkeypatch):
    monkeypatch.setenv("CREDIT_RATE_VND", "abc")
    with pytest.raises(ConfigError):
        load_settings(env_file=None)


def test_load_defaults_without_dotenv():
    assert load_settings(env_file=None) == Settings()


@pytest.mark.parametrize("provider", ["stub", "template"])
def test_offline_providers_need_no_key(monkeypatch, provider):
    monkeypatch.setenv("LLM_PROVIDER", provider)
    assert load_settings(env_file=None).llm_api_key is None


def test_dotenv_and_existing_environment_precedence(monkeypatch, tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("CREDIT_RATE_VND=600000\nLOG_LEVEL=debug\nMAX_CREDITS=25\n", encoding="utf-8")
    monkeypatch.setenv("CREDIT_RATE_VND", "500000")
    settings = load_settings(env_file)
    assert settings.credit_rate_vnd == 500_000
    assert settings.log_level == "DEBUG"
    assert settings.max_credits == 25
    assert settings.retake_multiplier == 1.5


@pytest.mark.parametrize(
    ("name", "value", "field"),
    [
        ("CREDIT_RATE_VND", "0", "credit_rate_vnd"),
        ("CREDIT_RATE_VND", "-1", "credit_rate_vnd"),
        ("CREDIT_RATE_VND", "1.5", "credit_rate_vnd"),
        ("MAX_CREDITS", "0", "max_credits"),
        ("MAX_CREDITS", "-1", "max_credits"),
        ("MAX_CREDITS", "abc", "max_credits"),
        ("RETAKE_MULTIPLIER", "0", "retake_multiplier"),
        ("RETAKE_MULTIPLIER", "-1", "retake_multiplier"),
        ("RETAKE_MULTIPLIER", "nan", "retake_multiplier"),
        ("RETAKE_MULTIPLIER", "inf", "retake_multiplier"),
        ("RETAKE_MULTIPLIER", "abc", "retake_multiplier"),
        ("LOG_LEVEL", "SENSITIVE_INVALID_VALUE", "log_level"),
    ],
)
def test_invalid_environment_has_safe_config_error(monkeypatch, name, value, field):
    monkeypatch.setenv(name, value)
    monkeypatch.setenv("LLM_API_KEY", "secret-never-display")
    with pytest.raises(ConfigError, match=field) as error:
        load_settings(env_file=None)
    assert "secret-never-display" not in str(error.value)
    assert "SENSITIVE_INVALID_VALUE" not in str(error.value)


def test_api_key_excluded_from_repr_and_serialization():
    settings = Settings(llm_api_key="fake-sensitive-key")
    assert "fake-sensitive-key" not in repr(settings)
    assert "llm_api_key" not in settings.model_dump()
    assert "fake-sensitive-key" not in settings.model_dump_json()


def test_dotenv_read_error_is_config_error(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_bytes(b"\xff\xfe")
    with pytest.raises(ConfigError, match="Cannot read"):
        load_settings(env_file)


def test_programming_errors_are_not_hidden(monkeypatch):
    def broken_loader(*args, **kwargs):
        raise RuntimeError("unexpected programming error")

    monkeypatch.setattr("assistant_core.config.load_dotenv", broken_loader)
    with pytest.raises(RuntimeError, match="programming error"):
        load_settings()


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
