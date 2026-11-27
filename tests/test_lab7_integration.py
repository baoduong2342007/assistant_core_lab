"""Live FastAPI and file-backed SQLite checks adapted from Minh's Lab 07 PR #57."""

from pathlib import Path

from fastapi.testclient import TestClient

from assistant_api.db import make_engine as real_make_engine
from assistant_api.main import create_app
from assistant_core.config import Settings


def test_api_sqlite_persistence_and_domain_queries(tmp_path: Path, monkeypatch):
    # Bypass conftest's isolated_api_database fixture so create_app opens our explicit temp SQLite file.
    monkeypatch.setattr("assistant_api.main.make_engine", real_make_engine)
    db_file = tmp_path / "lab7_persistence.db"
    settings = Settings(
        data_dir=Path(__file__).resolve().parents[1] / "data",
        llm_provider="stub",
        database_url=f"sqlite:///{db_file}",
        api_admin_key="lab7-admin-key",
    )

    app1 = create_app(settings=settings)
    with TestClient(app1) as client1:
        assert client1.get("/health").status_code == 200

        thesis = client1.post(
            "/v1/chat",
            json={"message": "Can I register my thesis with 118 credits?", "session_id": "s-persist"},
        )
        assert thesis.status_code == 200
        thesis_body = thesis.json()
        assert "H26#5.3" in [s["id"] for s in thesis_body["sources"]]

        card = client1.post("/v1/chat", json={"message": "I lost my student card", "session_id": "s-persist"})
        assert card.status_code == 200
        card_body = card.json()
        assert "S26#3" in [s["id"] for s in card_body["sources"]]

        tuition = client1.post(
            "/v1/chat",
            json={"message": "Tuition for 18 credits and 2 retake", "session_id": "s-persist"},
        )
        assert tuition.status_code == 200
        tuition_answer = tuition.json()["answer"]
        assert "9,450,000" in tuition_answer or "9.450.000" in tuition_answer

        unknown = client1.post(
            "/v1/chat",
            json={"message": "what is the capital of France", "session_id": "s-persist"},
        )
        assert unknown.status_code == 200
        unknown_body = unknown.json()
        assert unknown_body["path"] == "abstain"
        assert unknown_body["escalate"] is True
        assert unknown_body["sources"] == []

        fb_ok = client1.post(
            "/v1/feedback",
            json={"request_id": thesis_body["request_id"], "rating": -1, "comment": "needs clearer rule"},
        )
        assert fb_ok.status_code == 201
        fb_positive = client1.post("/v1/feedback", json={"request_id": card_body["request_id"], "rating": 1})
        assert fb_positive.status_code == 201

        fb_missing = client1.post(
            "/v1/feedback",
            json={"request_id": "nonexistent-request-id", "rating": 1},
        )
        assert fb_missing.status_code == 404

    assert db_file.exists()

    # Open a brand-new create_app instance against the same SQLite DB file and confirm persistence.
    app2 = create_app(settings=settings)
    with TestClient(app2) as client2:
        listed = client2.get("/v1/feedback", headers={"X-API-Key": "lab7-admin-key"})
        assert listed.status_code == 200
        items = listed.json()
        assert len(items) == 2
        by_request = {item["request_id"]: item for item in items}
        assert by_request[thesis_body["request_id"]]["rating"] == -1
        assert by_request[thesis_body["request_id"]]["comment"] == "needs clearer rule"
        assert by_request[card_body["request_id"]]["rating"] == 1
