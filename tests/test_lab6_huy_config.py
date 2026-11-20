"""Huy's Lab06 settings contract, including legacy CLI secret preservation."""

import os

import pytest
from pydantic import ValidationError

from assistant_core.config import Settings, load_settings
from assistant_core.errors import ConfigError
from assistant_core.models import Intent, Response

LAB6_ENV = (
    "LLM_PROVIDER",
    "LLM_API_KEY",
    "LLM_MODEL",
    "LLM_BASE_URL",
    "LLM_TIMEOUT_S",
    "KB_DIR",
    "RETRIEVAL_KIND",
    "RETRIEVAL_MIN_SCORE",
    "PROMPT_VERSION",
    "SESSION_SALT",
    "API_ADMIN_KEY",
    "CREDIT_RATE_VND",
    "LOG_LEVEL",
)


@pytest.fixture(autouse=True)
def isolated_lab6_environment(monkeypatch):
    monkeypatch.setattr(os, "environ", os.environ.copy())
    for name in LAB6_ENV:
        monkeypatch.delenv(name, raising=False)


def test_lab6_defaults_are_offline():
    settings = load_settings(env_file=None)
    assert settings.llm_provider == "stub" and settings.llm_api_key is None
    assert settings.llm_model == "llama3.2" and settings.llm_base_url is None
    assert settings.llm_timeout_s == 5.0 and settings.kb_dir is None
    assert settings.retrieval_kind == "bm25" and settings.retrieval_min_score == 2.0
    assert settings.prompt_version == "answer_v1"


@pytest.mark.parametrize("provider", ["stub", "template", "ollama", "openai"])
def test_supported_provider_configuration(monkeypatch, provider):
    monkeypatch.setenv("LLM_PROVIDER", provider)
    if provider == "openai":
        monkeypatch.setenv("LLM_API_KEY", "synthetic-key")
    assert load_settings(env_file=None).llm_provider == provider


@pytest.mark.parametrize("key", [None, "", "  "])
def test_openai_requires_nonblank_key(monkeypatch, key):
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    if key is not None:
        monkeypatch.setenv("LLM_API_KEY", key)
    with pytest.raises(ConfigError, match="llm_api_key"):
        load_settings(env_file=None)
    with pytest.raises(ValidationError):
        Settings(llm_provider="openai", llm_api_key=key)


@pytest.mark.parametrize("environment_wins", [False, True])
def test_lab6_dotenv_precedence(monkeypatch, tmp_path, environment_wins):
    env_file = tmp_path / ".env"
    env_file.write_text(
        "LLM_PROVIDER=ollama\nLLM_MODEL=local-demo\nLLM_BASE_URL=http://localhost:11434/\n"
        "LLM_TIMEOUT_S=12\nKB_DIR=custom/kb\nRETRIEVAL_KIND=hybrid\n"
        "RETRIEVAL_MIN_SCORE=0.25\nPROMPT_VERSION=answer_v1\nLLM_API_KEY=dotenv-key\n",
        encoding="utf-8",
    )
    if environment_wins:
        monkeypatch.setenv("LLM_MODEL", "environment-model")
        monkeypatch.setenv("LLM_API_KEY", "environment-key")
        monkeypatch.setenv("RETRIEVAL_MIN_SCORE", "0")
    settings = load_settings(env_file)
    assert settings.llm_provider == "ollama"
    assert settings.llm_model == ("environment-model" if environment_wins else "local-demo")
    assert settings.llm_api_key == ("environment-key" if environment_wins else "dotenv-key")
    assert settings.llm_base_url == "http://localhost:11434"
    assert settings.llm_timeout_s == 12
    assert str(settings.kb_dir) == "custom/kb"
    assert settings.retrieval_kind == "hybrid"
    assert settings.retrieval_min_score == (0 if environment_wins else 0.25)


@pytest.mark.parametrize(
    ("name", "value", "field"),
    [
        ("LLM_PROVIDER", "unrecognised", "llm_provider"),
        ("LLM_MODEL", " ", "llm_model"),
        ("LLM_BASE_URL", "not-a-url", "llm_base_url"),
        ("LLM_BASE_URL", "ftp://example.test", "llm_base_url"),
        ("LLM_BASE_URL", "https://user:private-password@example.test/v1", "llm_base_url"),
        ("LLM_BASE_URL", "https://example.test/v1?key=private-query", "llm_base_url"),
        ("LLM_BASE_URL", "https://example.test/v1#fragment", "llm_base_url"),
        ("LLM_TIMEOUT_S", "0", "llm_timeout_s"),
        ("LLM_TIMEOUT_S", "-1", "llm_timeout_s"),
        ("LLM_TIMEOUT_S", "nan", "llm_timeout_s"),
        ("LLM_TIMEOUT_S", "inf", "llm_timeout_s"),
        ("LLM_TIMEOUT_S", "abc", "llm_timeout_s"),
        ("RETRIEVAL_KIND", "unknown", "retrieval_kind"),
        ("RETRIEVAL_MIN_SCORE", "-1", "retrieval_min_score"),
        ("RETRIEVAL_MIN_SCORE", "nan", "retrieval_min_score"),
        ("RETRIEVAL_MIN_SCORE", "inf", "retrieval_min_score"),
        ("PROMPT_VERSION", "../../private", "prompt_version"),
    ],
)
def test_invalid_lab6_environment_is_reported_safely(monkeypatch, name, value, field):
    monkeypatch.setenv("LLM_API_KEY", "synthetic-secret-key")
    monkeypatch.setenv("SESSION_SALT", "synthetic-private-salt")
    monkeypatch.setenv(name, value)
    with pytest.raises(ConfigError, match=field) as error:
        load_settings(env_file=None)
    for secret in ("synthetic-secret-key", "synthetic-private-salt", "private-password", "private-query"):
        assert secret not in str(error.value)


def test_cli_overrides_preserve_all_secrets(monkeypatch, capsys):
    from assistant_core.__main__ import main

    original = Settings(
        llm_provider="openai",
        llm_api_key="synthetic-llm-secret",
        api_admin_key="synthetic-admin-secret",
        session_salt="synthetic-session-secret",
    )
    captured = []

    class Service:
        def handle(self, message):
            return Response(answer="Hello", intent=Intent.GREETING)

    def factory(settings, fail_provider=False):
        captured.append(settings)
        return Service()

    monkeypatch.setattr("assistant_core.__main__.load_settings", lambda: original)
    monkeypatch.setattr("assistant_core.__main__.build_service", factory)
    assert main(["--log-level", "warning", "--credit-rate", "500000", "hello"]) == 0
    updated = captured[0]
    assert updated.log_level == "WARNING" and updated.credit_rate_vnd == 500000
    output = capsys.readouterr()
    for name in ("llm_api_key", "api_admin_key", "session_salt"):
        secret = getattr(original, name)
        assert getattr(updated, name) == secret
        assert name not in updated.model_dump()
        assert secret not in repr(updated) + updated.model_dump_json() + output.out + output.err
