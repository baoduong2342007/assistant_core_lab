import logging
import os
import sqlite3
from contextlib import closing
from importlib.util import find_spec
from inspect import signature

import pytest

from assistant_core.config import Settings


@pytest.fixture
def persistence():
    if find_spec("assistant_api.db") is None:
        pytest.skip("Requires the Lab05 repository from Bảo's integration branch")
    from assistant_api import db

    return db


def test_session_hash_is_stable_and_depends_on_salt(persistence):
    raw = "phiên-thử-01"
    salt = "lab-salt"
    assert persistence.hash_session(raw, salt) == "749d72b8f8545c55"
    assert persistence.hash_session(raw, "another-salt") != "749d72b8f8545c55"


def test_session_reuse_and_isolation_across_databases(persistence):
    from sqlmodel import Session, select

    settings = Settings(database_url="sqlite:///:memory:", session_salt="memory-test-salt")
    first = persistence.make_engine(settings.database_url)
    second = persistence.make_engine(settings.database_url)
    try:
        persistence.init_db(first)
        persistence.init_db(second)
        repo = persistence.Repository(first, settings.session_salt)
        repo.record_interaction("synthetic-session", "request-1", "greeting", None, True, False, 2.0)
        repo.record_interaction("synthetic-session", "request-2", "greeting", None, True, False, 3.0)

        expected = persistence.hash_session("synthetic-session", settings.session_salt)
        with Session(first) as db:
            assert db.exec(select(persistence.ChatSession.id)).all() == [expected]
            assert set(db.exec(select(persistence.Interaction.request_id, persistence.Interaction.session_id))) == {
                ("request-1", expected),
                ("request-2", expected),
            }
        with Session(second) as db:
            assert db.exec(select(persistence.ChatSession.id)).all() == []
            assert db.exec(select(persistence.Interaction.id)).all() == []
    finally:
        first.dispose()
        second.dispose()


def test_api_stores_only_session_hash_and_chat_metadata(persistence, monkeypatch, tmp_path, project_root, caplog):
    from fastapi.testclient import TestClient

    from assistant_api.main import create_app

    if "repo" not in signature(create_app).parameters:
        pytest.skip("Requires the Lab05 API integration from Dương's branch")

    path = tmp_path / "privacy.db"
    salt = "test-only-privacy-salt-9cf2"
    raw_session = "test-only-raw-session-a49f"
    raw_message = "test-only-private-chat-content-83ac"
    monkeypatch.setattr(os, "environ", os.environ.copy())
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{path}")
    monkeypatch.setenv("SESSION_SALT", salt)
    monkeypatch.setenv("ASSISTANT_DATA_DIR", str(project_root / "data"))
    caplog.set_level(logging.INFO)
    # Use the actual engine factory even if older API tests override it for isolation.
    monkeypatch.setattr("assistant_api.main.make_engine", persistence.make_engine)
    request_ids = []
    for _ in range(2):
        with TestClient(create_app()) as client:
            response = client.post("/v1/chat", json={"message": raw_message, "session_id": raw_session})
            assert response.status_code == 200
            request_ids.append(response.json()["request_id"])

    expected = persistence.hash_session(raw_session, salt)
    with closing(sqlite3.connect(path)) as connection:
        assert connection.execute("SELECT id FROM chat_session").fetchall() == [(expected,)]
        assert connection.execute("SELECT request_id, session_id FROM interaction ORDER BY id").fetchall() == [
            (request_id, expected) for request_id in request_ids
        ]
        snapshot = "\n".join(connection.iterdump())

    content = path.read_bytes()
    for private_value in (raw_session, raw_message, salt):
        assert private_value not in snapshot
        assert private_value.encode() not in content
        assert private_value not in caplog.text
