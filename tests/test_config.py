"""Unit tests for configuration management."""

from pathlib import Path

import pytest
from pydantic import ValidationError

from assistant_core.config import Settings, load_settings
from assistant_core.errors import ConfigError


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


def test_load_settings_missing_api_key_when_provider_not_stub(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    with pytest.raises(ConfigError, match="LLM_API_KEY is required"):
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
