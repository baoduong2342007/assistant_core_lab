from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from streamlit.testing.v1 import AppTest

from assistant_api.db import make_engine as real_make_engine
from assistant_api.main import create_app
from assistant_core.config import Settings
from ui.api_client import ChatResult
from ui.logic import EXAMPLES, WELCOME

PROJECT_ROOT = Path(__file__).resolve().parents[1]
APP_PATH = PROJECT_ROOT / "ui" / "app.py"


@dataclass
class FakeAssistantClient:
    is_healthy: bool = True
    feedback_ok: bool = True
    next_result: ChatResult = field(
        default_factory=lambda: ChatResult(
            ok=True,
            answer="Student Affairs office is in room I.102.",
            intent="rule",
            sources=[{"id": "S26#3", "title": "3 Student card replacement"}],
            path="deterministic",
            escalate=False,
            degraded=False,
            request_id="req-ui-001",
        )
    )
    ask_calls: list[tuple[str, str]] = field(default_factory=list)
    feedback_calls: list[tuple[str, int, str | None]] = field(default_factory=list)

    closed_runs: int = 0

    def __enter__(self) -> FakeAssistantClient:
        return self

    def __exit__(self, *_: object) -> None:
        self.closed_runs += 1

    def healthy(self) -> bool:
        return self.is_healthy

    def ask(self, message: str, session_id: str) -> ChatResult:
        self.ask_calls.append((message, session_id))
        return self.next_result

    def send_feedback(self, request_id: str, rating: int, comment: str | None = None) -> bool:
        self.feedback_calls.append((request_id, rating, comment))
        return self.feedback_ok


@pytest.fixture
def fake_client(monkeypatch) -> FakeAssistantClient:
    client = FakeAssistantClient()
    monkeypatch.setattr("ui.api_client.AssistantClient", lambda *args, **kwargs: client)
    return client


def _button_by_label(at: AppTest, label: str):
    return next(btn for btn in at.button if btn.label == label)


def test_app_welcome_and_backend_unreachable(fake_client: FakeAssistantClient):
    fake_client.is_healthy = False
    at = AppTest.from_file(str(APP_PATH)).run()

    assert not at.exception
    assert WELCOME in [m.value for m in at.chat_message[0].markdown]
    assert len(at.error) == 1
    assert "not reachable" in at.error[0].value.lower()


def test_app_sidebar_example_click_sends_one_ask(fake_client: FakeAssistantClient):
    at = AppTest.from_file(str(APP_PATH)).run()
    assert len(at.error) == 0

    at.sidebar.button[0].click().run()

    assert not at.exception
    assert fake_client.closed_runs >= 2
    assert len(fake_client.ask_calls) == 1
    assert fake_client.ask_calls[0][0] == EXAMPLES[0]
    assert len(at.chat_message) == 3
    assert EXAMPLES[0] in [m.value for m in at.chat_message[1].markdown]
    assert fake_client.next_result.answer in [m.value for m in at.chat_message[2].markdown]


def test_app_whitespace_only_input_warns_and_does_not_call_ask(fake_client: FakeAssistantClient):
    at = AppTest.from_file(str(APP_PATH)).run()
    at.chat_input[0].set_value("   \t  ").run()

    assert not at.exception
    assert len(fake_client.ask_calls) == 0
    assert any("Please type a question." in w.value for w in at.warning)


def test_app_valid_padded_input_strips_before_ask(fake_client: FakeAssistantClient):
    at = AppTest.from_file(str(APP_PATH)).run()
    at.chat_input[0].set_value("  Can I register my thesis with 118 credits?  ").run()

    assert not at.exception
    assert len(fake_client.ask_calls) == 1
    assert fake_client.ask_calls[0][0] == "Can I register my thesis with 118 credits?"
    assert "Can I register my thesis with 118 credits?" in [m.value for m in at.chat_message[1].markdown]


@pytest.mark.parametrize(("label", "expected_rating"), [("👍 Helpful", 1), ("👎 Not helpful", -1)])
def test_app_feedback_success_shows_toast_hides_buttons_and_no_resend(
    fake_client: FakeAssistantClient,
    label: str,
    expected_rating: int,
):
    at = AppTest.from_file(str(APP_PATH)).run()
    at.chat_input[0].set_value("I lost my student card").run()

    _button_by_label(at, label).click().run()

    assert not at.exception
    assert fake_client.feedback_calls == [("req-ui-001", expected_rating, None)]
    assert "req-ui-001" in at.session_state["rated"]
    assert len(at.toast) == 1
    assert "Thanks" in at.toast[0].value
    assert {"👍 Helpful", "👎 Not helpful"}.isdisjoint({b.label for b in at.button})
    assert any("Feedback recorded" in c.value for c in at.caption)

    # Subsequent rerun keeps the feedback buttons hidden and does not re-send feedback.
    at.run()
    assert {"👍 Helpful", "👎 Not helpful"}.isdisjoint({b.label for b in at.button})
    assert len(fake_client.feedback_calls) == 1


@pytest.mark.parametrize("label", ["👍 Helpful", "👎 Not helpful"])
def test_app_feedback_failure_shows_retry_warning_and_keeps_buttons(
    fake_client: FakeAssistantClient,
    label: str,
):
    fake_client.feedback_ok = False
    at = AppTest.from_file(str(APP_PATH)).run()
    at.chat_input[0].set_value("I lost my student card").run()

    _button_by_label(at, label).click().run()

    assert not at.exception
    assert len(at.toast) == 0
    assert "req-ui-001" not in at.session_state["rated"]
    assert any("try again" in w.value.lower() for w in at.warning)
    remaining_labels = {b.label for b in at.button}
    assert {"👍 Helpful", "👎 Not helpful"}.issubset(remaining_labels)

    # User can retry once the backend recovers.
    fake_client.feedback_ok = True
    _button_by_label(at, label).click().run()
    assert len(at.toast) == 1
    assert "req-ui-001" in at.session_state["rated"]
    assert {"👍 Helpful", "👎 Not helpful"}.isdisjoint({b.label for b in at.button})
    at.run()
    assert {"👍 Helpful", "👎 Not helpful"}.isdisjoint({b.label for b in at.button})


def test_app_vietnamese_escalation_hint_and_new_chat_reset(fake_client: FakeAssistantClient):
    fake_client.next_result = ChatResult(
        ok=True,
        answer="I'm not confident I can answer that. Please contact the Training Office (room I.101).",
        intent="unknown",
        path="abstain",
        escalate=True,
        request_id="req-vi-001",
    )
    at = AppTest.from_file(str(APP_PATH)).run()
    initial_session = at.session_state["session_id"]

    at.chat_input[0].set_value("Nếu bị mất thẻ sinh viên thì đến đâu để làm lại?").run()
    assert not at.exception
    assert len(at.chat_message) == 3
    assert any("English only" in box.value for box in at.info)

    _button_by_label(at, "New chat").click().run()
    assert not at.exception
    assert len(at.chat_message) == 1
    assert len(at.session_state["rated"]) == 0
    assert at.session_state["session_id"] != initial_session


def test_api_sqlite_persistence_and_domain_queries(tmp_path: Path, monkeypatch):
    # Bypass conftest's isolated_api_database fixture so create_app opens our explicit temp SQLite file.
    monkeypatch.setattr("assistant_api.main.make_engine", real_make_engine)
    db_file = tmp_path / "lab7_persistence.db"
    settings = Settings(
        data_dir=PROJECT_ROOT / "data",
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
        assert "S26#3" in [s["id"] for s in card.json()["sources"]]

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
        assert len(items) == 1
        assert items[0]["request_id"] == thesis_body["request_id"]
        assert items[0]["rating"] == -1
        assert items[0]["comment"] == "needs clearer rule"
