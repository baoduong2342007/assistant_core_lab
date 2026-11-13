import logging
import os

import pytest

from assistant_core.config import Settings, load_settings
from assistant_core.errors import ConfigError


@pytest.fixture(autouse=True)
def isolated_environment(monkeypatch):
    monkeypatch.setattr(os, "environ", os.environ.copy())
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("SESSION_SALT", raising=False)


def test_persistence_defaults():
    settings = load_settings(env_file=None)
    assert settings.database_url == Settings().database_url == "sqlite:///assistant.db"
    assert settings.session_salt == Settings().session_salt
    assert settings.session_salt.strip()


@pytest.mark.parametrize("prefer_environment", [False, True])
def test_persistence_env_precedence(monkeypatch, tmp_path, prefer_environment):
    env_file = tmp_path / ".env"
    env_file.write_text("DATABASE_URL=sqlite:///dotenv.db\nSESSION_SALT=dotenv-test-salt\n", encoding="utf-8")
    if prefer_environment:
        monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
        monkeypatch.setenv("SESSION_SALT", "environment-test-salt")
        expected = ("sqlite:///:memory:", "environment-test-salt")
    else:
        expected = ("sqlite:///dotenv.db", "dotenv-test-salt")

    settings = load_settings(env_file)
    assert (settings.database_url, settings.session_salt) == expected


def test_salt_excluded_from_repr_and_serialization():
    salt = "synthetic-secret-that-must-stay-private"
    settings = Settings(session_salt=salt)
    assert settings.session_salt == salt
    assert salt not in repr(settings)
    assert salt not in str(settings)
    assert "session_salt" not in settings.model_dump()
    assert "session_salt" not in settings.model_dump_json()


@pytest.mark.parametrize(("variable", "field"), [("DATABASE_URL", "database_url"), ("SESSION_SALT", "session_salt")])
@pytest.mark.parametrize("value", ["", "  "])
def test_blank_persistence_setting_is_rejected(monkeypatch, variable, field, value):
    monkeypatch.setenv(variable, value)
    with pytest.raises(ConfigError, match=rf"^Invalid configuration: {field}$"):
        load_settings(env_file=None)


def test_configuration_error_keeps_salt_out_of_logs(monkeypatch, caplog):
    salt = "synthetic-secret-that-must-stay-out-of-logs"
    monkeypatch.setenv("SESSION_SALT", salt)
    monkeypatch.setenv("DATABASE_URL", "")
    with pytest.raises(ConfigError, match="database_url") as failure:
        load_settings(env_file=None)

    logging.getLogger(__name__).error("Startup failed", exc_info=failure.value)
    assert "Invalid configuration: database_url" in caplog.text
    assert salt not in caplog.text
