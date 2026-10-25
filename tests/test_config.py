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
