from fastapi.testclient import TestClient
from sqlmodel import Session, select

from assistant_api.db import ChatSession, Interaction, Repository, init_db, make_engine
from assistant_api.main import create_app


def test_api_persistence_and_privacy_across_restart(tmp_path, sample_settings, service):
    url = f"sqlite:///{tmp_path / 'restart.db'}"
    settings = sample_settings.model_copy(update={"api_admin_key": "admin"})
    engine = make_engine(url)
    init_db(engine)
    repo = Repository(engine, "test-secret")
    with TestClient(create_app(settings, service, repo=repo)) as client:
        request_id = client.post(
            "/v1/chat", json={"message": "hello private message", "session_id": "raw-session"}
        ).json()["request_id"]
        assert client.post("/v1/feedback", json={"request_id": request_id, "rating": 1}).status_code == 201
        assert client.post("/v1/feedback", json={"request_id": "unknown", "rating": 1}).status_code == 404
        assert client.get("/v1/stats").status_code == 401
    with Session(engine) as db:
        session = db.exec(select(ChatSession)).one()
        interaction = db.exec(select(Interaction)).one()
        assert session.id != "raw-session"
        assert interaction.request_id == request_id
    engine.dispose()
    engine2 = make_engine(url)
    with TestClient(create_app(settings, service, repo=Repository(engine2, "test-secret"))) as client:
        result = client.get("/v1/feedback", headers={"X-Admin-Key": "admin"})
        assert result.status_code == 200
        assert result.json()[0]["request_id"] == request_id
        assert client.get("/v1/stats", headers={"X-API-Key": "admin"}).status_code == 200
    engine2.dispose()
    content = (tmp_path / "restart.db").read_bytes()
    assert b"raw-session" not in content
    assert b"hello private message" not in content


def test_parallel_first_requests_share_session(tmp_path):
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier

    from sqlalchemy import event

    engine = make_engine(f"sqlite:///{tmp_path / 'parallel.db'}")
    init_db(engine)
    barrier = Barrier(2)

    @event.listens_for(engine, "before_cursor_execute")
    def synchronize_inserts(conn, cursor, statement, parameters, context, executemany):
        if statement.lstrip().upper().startswith("INSERT INTO CHAT_SESSION"):
            barrier.wait(timeout=10)

    repo = Repository(engine, "salt")
    with ThreadPoolExecutor(max_workers=2) as pool:
        list(pool.map(lambda n: repo.record_interaction("same", str(n), "greeting", None, True, False, 1), range(2)))
    with Session(engine) as db:
        assert len(db.exec(select(ChatSession)).all()) == 1
        assert len(db.exec(select(Interaction)).all()) == 2
    engine.dispose()


def test_database_settings_from_environment_are_private(monkeypatch):
    from assistant_core.config import load_settings

    monkeypatch.setenv("DATABASE_URL", "sqlite:///custom.db")
    monkeypatch.setenv("SESSION_SALT", "private-test-salt")
    settings = load_settings(env_file=None)
    assert settings.database_url == "sqlite:///custom.db"
    assert settings.session_salt == "private-test-salt"
    assert "private-test-salt" not in repr(settings)
    assert "session_salt" not in settings.model_dump()
