"""AppTest exercises real UI reruns while MockTransport replaces only HTTP."""

import json
from pathlib import Path

import httpx
import pytest
from streamlit.testing.v1 import AppTest

from ui.api_client import AssistantClient, ChatResult
from ui.logic import format_sources, status_note

APP = Path(__file__).resolve().parents[1] / "ui/app.py"


@pytest.fixture
def ui(monkeypatch):
    state = {"requests": [], "feedback_status": 201, "chat_status": 200, "online": True}

    def handler(request):
        if not state["online"]:
            raise httpx.ConnectError("refused", request=request)
        if request.url.path == "/health":
            return httpx.Response(200)
        body = json.loads(request.content)
        state["requests"].append((request.url.path, body))
        if request.url.path == "/v1/feedback":
            return httpx.Response(state["feedback_status"])
        number = sum(path == "/v1/chat" for path, _ in state["requests"])
        return httpx.Response(
            state["chat_status"],
            json={
                "answer": "At least 120 credits and GPA 2.0.",
                "intent": "rule",
                "sources": [{"id": "H26#5.3", "title": "Thesis registration"}],
                "request_id": f"request-{number}",
                "degraded": False,
                "escalate": False,
            },
        )

    monkeypatch.setattr(
        "ui.api_client.AssistantClient", lambda: AssistantClient(transport=httpx.MockTransport(handler))
    )
    app = AppTest.from_file(str(APP)).run()
    assert not app.exception
    return app, state


def test_sidebar_and_chat_share_one_post_path_and_keep_session(ui):
    app, state = ui
    session = app.session_state.session_id
    app.sidebar.button[0].click().run()
    assert not app.exception and len(state["requests"]) == 1
    assert state["requests"][0][1]["message"] == "Can I register my thesis with 118 credits?"
    app.run()
    assert len(state["requests"]) == 1
    app.chat_input[0].set_value("  Another question  ").run()
    assert len(state["requests"]) == 2
    assert state["requests"][1][1] == {"message": "Another question", "session_id": session}
    assert app.session_state.session_id == session and len(app.chat_message) == 5
    assert any("H26#5.3" in caption.value for caption in app.caption)


@pytest.mark.parametrize("value", ["   ", "x" * 2001])
def test_invalid_chat_does_not_post(ui, value):
    app, state = ui
    app.chat_input[0].set_value(value).run()
    assert not state["requests"] and app.warning and not app.exception


@pytest.mark.parametrize(("key", "rating"), [("up-request-1", 1), ("down-request-1", -1)])
def test_feedback_success_hides_both_buttons_and_does_not_repeat(ui, key, rating):
    app, state = ui
    app.sidebar.button[0].click().run()
    app.button(key=key).click().run()
    assert state["requests"][-1] == ("/v1/feedback", {"request_id": "request-1", "rating": rating, "comment": None})
    assert "request-1" in app.session_state.rated and len(app.success) == 1
    assert all(button.key not in ("up-request-1", "down-request-1") for button in app.button)
    app.run()
    assert len(state["requests"]) == 2 and not app.exception


@pytest.mark.parametrize("status", [404, 500])
def test_feedback_failure_keeps_buttons_and_retry_can_succeed(ui, status):
    app, state = ui
    app.sidebar.button[0].click().run()
    state["feedback_status"] = status
    app.button(key="down-request-1").click().run()
    assert "request-1" not in app.session_state.rated and app.error and not app.success
    state["feedback_status"] = 201
    app.button(key="down-request-1").click().run()
    assert "request-1" in app.session_state.rated and app.success and not app.error
    assert len(state["requests"]) == 3 and not app.exception


def test_backend_outage_preserves_history_and_recovers(ui):
    app, state = ui
    app.sidebar.button[0].click().run()
    history = list(app.session_state.messages)
    state["online"] = False
    app.run()
    assert app.error and app.session_state.messages == history
    app.chat_input[0].set_value("New question").run()
    assert "Cannot reach" in app.session_state.messages[-1]["content"]
    state["online"] = True
    app.chat_input[0].set_value("Question after recovery").run()
    assert app.session_state.messages[-1]["request_id"] == "request-2"
    assert not app.exception


def test_separate_sessions_do_not_share_history(ui):
    first, _ = ui
    first.sidebar.button[0].click().run()
    second = AppTest.from_file(str(APP)).run()
    assert first.session_state.session_id != second.session_state.session_id
    assert len(second.session_state.messages) == 1 and len(first.session_state.messages) == 3


def test_source_rendering_and_escalation_take_priority_over_degraded():
    assert format_sources([]) == ""
    assert (
        format_sources([{"id": "H#1", "title": "One"}, {"id": "S#2", "title": "Two"}])
        == "Sources: H#1 — One; S#2 — Two"
    )
    assert "I.101" in status_note(ChatResult(ok=True, escalate=True, degraded=True))
    assert "directly from the source" in status_note(ChatResult(ok=True, degraded=True))
    assert status_note(ChatResult(ok=True)) is None
