"""Lab 07 tests for Bảo (`simble2k`): F1 feedback flow, error recovery, UI bonus, and SQLite persistence."""

from __future__ import annotations

import json
from pathlib import Path

import httpx
import pytest
from fastapi.testclient import TestClient
from streamlit.testing.v1 import AppTest

from assistant_api.db import make_engine as real_make_engine
from assistant_api.main import create_app
from assistant_core.config import Settings
from ui.api_client import AssistantClient, ChatResult
from ui.logic import format_sources, source_items, status_note

APP_PATH = Path(__file__).resolve().parents[1] / "ui/app.py"


def _mock_client(handler) -> AssistantClient:
    return AssistantClient("http://api.test", transport=httpx.MockTransport(handler))


def test_logic_sources_bonus_and_escalation_priority():
    assert format_sources([{"id": "H26#5.3", "title": "Thesis"}, {"id": "S26#3", "title": "Card"}]) == (
        "Sources: H26#5.3 — Thesis; S26#3 — Card"
    )
    items = source_items(
        [
            {"id": "H26#5.3", "title": "Thesis registration"},
            {"id": "S26#3", "title": "Student card replacement"},
            {"id": "F26#1", "title": "Tuition rules"},
            {"id": "OTHER#9", "title": "Extra notice"},
        ]
    )
    assert [item["category"] for item in items] == [
        "Student Handbook",
        "Campus Services",
        "Tuition & Fees",
        "Official Document",
    ]
    escalated = status_note(ChatResult(ok=True, escalate=True, degraded=True))
    assert escalated is not None and "I.101" in escalated
    degraded_only = status_note(ChatResult(ok=True, escalate=False, degraded=True))
    assert degraded_only is not None and "source document" in degraded_only
    assert status_note(ChatResult(ok=True)) is None


def test_client_feedback_and_error_handling():
    captured: list[dict] = []

    def ok_handler(req: httpx.Request) -> httpx.Response:
        captured.append(json.loads(req.content))
        return httpx.Response(201, json={"id": 1})

    c_ok = _mock_client(ok_handler)
    assert c_ok.send_feedback("req-1", -1, comment="unclear") is True
    assert c_ok.last_feedback_error == ""
    assert captured == [{"request_id": "req-1", "rating": -1, "comment": "unclear"}]

    c_404 = _mock_client(lambda req: httpx.Response(404))
    assert c_404.send_feedback("missing", 1) is False
    assert "404" in c_404.last_feedback_error

    c_500 = _mock_client(lambda req: httpx.Response(500))
    assert c_500.send_feedback("req-1", -1) is False
    assert "500" in c_500.last_feedback_error

    def conn_err(req: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("down", request=req)

    c_down = _mock_client(conn_err)
    assert c_down.send_feedback("req-1", 1) is False
    assert "Cannot reach" in c_down.last_feedback_error
    assert c_down.healthy() is False and "not reachable" in c_down.health_error

    def timeout_err(req: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("slow", request=req)

    c_timeout = _mock_client(timeout_err)
    assert c_timeout.send_feedback("req-1", -1) is False
    assert "timed out" in c_timeout.last_feedback_error
    assert "taking too long" in c_timeout.ask("hello", "s1").error

    c_429 = _mock_client(lambda req: httpx.Response(429))
    assert "Too many questions" in c_429.ask("hello", "s1").error

    with pytest.raises(ValueError, match="http://"):
        AssistantClient("ftp://invalid-url")


@pytest.fixture
def mocked_ui(monkeypatch):
    state = {
        "requests": [],
        "feedback_status": 201,
        "feedback_connect_error": False,
        "online": True,
        "sources": [{"id": "H26#5.3", "title": "5.3 Thesis registration"}],
    }

    def handler(request: httpx.Request) -> httpx.Response:
        if not state["online"]:
            raise httpx.ConnectError("offline", request=request)
        if request.url.path == "/health":
            return httpx.Response(200, json={"status": "ok"})
        body = json.loads(request.content)
        state["requests"].append((request.url.path, body))
        if request.url.path == "/v1/feedback":
            if state["feedback_connect_error"]:
                raise httpx.ConnectError("feedback down", request=request)
            return httpx.Response(state["feedback_status"])
        chat_index = sum(1 for path, _ in state["requests"] if path == "/v1/chat")
        return httpx.Response(
            200,
            json={
                "answer": "Minimum 120 credits and GPA 2.0.",
                "intent": "rule",
                "sources": state["sources"],
                "degraded": False,
                "escalate": False,
                "path": "rag",
                "request_id": f"req-{chat_index}",
            },
        )

    monkeypatch.setattr(
        "ui.api_client.AssistantClient",
        lambda: AssistantClient(transport=httpx.MockTransport(handler)),
    )
    app = AppTest.from_file(str(APP_PATH)).run()
    assert not app.exception
    return app, state


def test_ui_sidebar_chat_strip_and_session_preserved(mocked_ui):
    app, state = mocked_ui
    sid = app.session_state.session_id
    app.sidebar.button[0].click().run()
    assert len(state["requests"]) == 1
    assert state["requests"][0][1]["message"] == "Can I register my thesis with 118 credits?"

    app.chat_input[0].set_value("   Where is the library?   ").run()
    assert len(state["requests"]) == 2
    assert state["requests"][1][1] == {"message": "Where is the library?", "session_id": sid}
    assert app.session_state.session_id == sid
    assert any("H26#5.3" in c.value for c in app.caption)
    assert any("Source details (1)" in exp.label for exp in app.expander)


@pytest.mark.parametrize("bad_text", ["   ", "a" * 2001])
def test_ui_invalid_input_does_not_post(mocked_ui, bad_text):
    app, state = mocked_ui
    app.chat_input[0].set_value(bad_text).run()
    assert state["requests"] == []
    assert len(app.warning) == 1


@pytest.mark.parametrize(
    ("button_key", "expected_rating", "expected_phrase"),
    [
        ("up-req-1", 1, "Thanks for your feedback!"),
        ("down-req-1", -1, "we will look at this answer"),
    ],
)
def test_ui_feedback_locks_after_201_and_does_not_repeat(mocked_ui, button_key, expected_rating, expected_phrase):
    app, state = mocked_ui
    app.sidebar.button[0].click().run()
    history_len_before = len(app.session_state.messages)

    app.button(key=button_key).click().run()
    assert state["requests"][-1] == (
        "/v1/feedback",
        {"request_id": "req-1", "rating": expected_rating, "comment": None},
    )
    assert "req-1" in app.session_state.rated
    assert any(expected_phrase in s.value for s in app.success)
    assert all(b.key not in ("up-req-1", "down-req-1") for b in app.button)
    assert len(app.session_state.messages) == history_len_before

    # Rerunning does not re-POST feedback.
    app.run()
    assert len(state["requests"]) == 2


@pytest.mark.parametrize("failure_mode", ["404", "500", "connect"])
def test_ui_feedback_failure_keeps_buttons_and_retries(mocked_ui, failure_mode):
    app, state = mocked_ui
    app.sidebar.button[0].click().run()

    if failure_mode == "connect":
        state["feedback_connect_error"] = True
    else:
        state["feedback_status"] = int(failure_mode)

    app.button(key="down-req-1").click().run()
    assert "req-1" not in app.session_state.rated
    assert len(app.error) == 1
    assert any(b.key == "down-req-1" for b in app.button)

    # Recover and retry succeeds.
    state["feedback_connect_error"] = False
    state["feedback_status"] = 201
    app.button(key="down-req-1").click().run()
    assert "req-1" in app.session_state.rated
    assert not app.error
    assert len(app.success) == 1


def test_ui_outage_preserves_history_and_no_expander_when_empty_sources(mocked_ui):
    app, state = mocked_ui
    state["sources"] = []
    app.chat_input[0].set_value("Tuition for 18 credits").run()
    assert not any("Source details" in exp.label for exp in app.expander)

    saved_messages = list(app.session_state.messages)
    state["online"] = False
    app.run()
    assert len(app.error) == 1
    assert app.session_state.messages == saved_messages


def test_api_feedback_sqlite_persistence_across_restart(tmp_path: Path, monkeypatch):
    # Bypass conftest's autouse isolated_api_database so both app instances share the same SQLite file.
    monkeypatch.setattr("assistant_api.main.make_engine", real_make_engine)
    db_path = tmp_path / "bao_feedback_persist.db"
    settings = Settings(
        data_dir=Path(__file__).resolve().parents[1] / "data",
        llm_provider="stub",
        database_url=f"sqlite:///{db_path}",
        api_admin_key="bao-lab7-admin",
    )

    app1 = create_app(settings=settings)
    with TestClient(app1) as client1:
        assert client1.get("/health").status_code == 200

        thesis = client1.post(
            "/v1/chat",
            json={"message": "Can I register my thesis with 118 credits?", "session_id": "bao-s1"},
        )
        assert thesis.status_code == 200
        thesis_body = thesis.json()
        assert "H26#5.3" in [s["id"] for s in thesis_body["sources"]]

        card = client1.post(
            "/v1/chat",
            json={"message": "I lost my student card", "session_id": "bao-s1"},
        )
        assert card.status_code == 200
        card_body = card.json()
        assert "S26#3" in [s["id"] for s in card_body["sources"]]

        fb_up = client1.post(
            "/v1/feedback",
            json={"request_id": card_body["request_id"], "rating": 1},
        )
        assert fb_up.status_code == 201

        fb_down = client1.post(
            "/v1/feedback",
            json={
                "request_id": thesis_body["request_id"],
                "rating": -1,
                "comment": "Need clearer credit threshold",
            },
        )
        assert fb_down.status_code == 201

        fb_missing = client1.post(
            "/v1/feedback",
            json={"request_id": "unknown-id-404", "rating": -1},
        )
        assert fb_missing.status_code == 404

    assert db_path.exists()

    # Start a brand-new FastAPI app pointing at the same SQLite database file.
    app2 = create_app(settings=settings)
    with TestClient(app2) as client2:
        resp = client2.get("/v1/feedback", headers={"X-API-Key": "bao-lab7-admin"})
        assert resp.status_code == 200
        rows = resp.json()
        assert len(rows) == 2
        by_req = {row["request_id"]: row for row in rows}
        assert by_req[card_body["request_id"]]["rating"] == 1
        assert by_req[thesis_body["request_id"]]["rating"] == -1
        assert by_req[thesis_body["request_id"]]["comment"] == "Need clearer credit threshold"
