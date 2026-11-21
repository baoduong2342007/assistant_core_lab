"""Offline contract checks for Huy's UI HTTP client."""

import json

import httpx
import pytest

from ui.api_client import DEFAULT_API_URL, AssistantClient, api_url

OK = {
    "answer": "Evidence",
    "intent": "rule",
    "sources": [{"id": "H26#5.3", "title": "Thesis registration"}],
    "path": "llm",
    "degraded": False,
    "escalate": False,
    "confidence": 0.7,
    "request_id": "request-1",
}


def test_ui_url_uses_ui_process_environment_and_explicit_override(monkeypatch):
    monkeypatch.delenv("ASSISTANT_API_URL", raising=False)
    assert api_url() == DEFAULT_API_URL
    monkeypatch.setenv("ASSISTANT_API_URL", "https://api.example.test/assistant/")
    assert api_url() == "https://api.example.test/assistant"
    assert api_url(" http://127.0.0.1:9000/ ") == "http://127.0.0.1:9000"


@pytest.mark.parametrize(
    "value",
    [
        "",
        "localhost:8000",
        "ftp://example.test",
        "http://user:secret@example.test",
        "https://example.test?key=secret",
        "https://example.test#fragment",
        "http://[",
    ],
)
def test_invalid_url_never_echoes_credentials(value):
    with pytest.raises(ValueError) as error:
        api_url(value)
    assert "secret" not in str(error.value)


@pytest.mark.parametrize("timeout", [0, -1, float("nan"), float("inf")])
def test_timeout_must_be_finite_and_positive(timeout):
    with pytest.raises(ValueError):
        AssistantClient(timeout_s=timeout)


def test_chat_request_and_full_response_contract():
    requests = []

    def handler(request):
        requests.append(request)
        return httpx.Response(200, json=OK)

    with AssistantClient("https://api.example.test/prefix/", 3.5, httpx.MockTransport(handler)) as client:
        result = client.ask("  question  ", "session-1")
    assert len(requests) == 1
    request = requests[0]
    assert request.method == "POST" and request.url.path == "/prefix/v1/chat"
    assert json.loads(request.content) == {"message": "question", "session_id": "session-1"}
    assert request.extensions["timeout"]["read"] == 3.5
    assert result.ok and result.request_id == "request-1" and result.confidence == 0.7
    assert result.sources == OK["sources"] and result.path == "llm"


@pytest.mark.parametrize("question", ["", "   ", "x" * 2001])
def test_invalid_question_sends_no_post(question):
    def unexpected(request):
        raise AssertionError("invalid question reached HTTP")

    with AssistantClient(transport=httpx.MockTransport(unexpected)) as client:
        assert not client.ask(question, "session").ok


@pytest.mark.parametrize(
    ("status", "message"), [(422, "type a question"), (429, "wait a minute"), (500, "error 500"), (503, "try again")]
)
def test_chat_http_errors_have_recovery_steps(status, message):
    requests = []

    def handler(request):
        requests.append(request)
        return httpx.Response(status, text="private upstream details")

    with AssistantClient(transport=httpx.MockTransport(handler)) as client:
        result = client.ask("question", "session")
    assert not result.ok and message in result.error
    assert "private upstream details" not in result.error and len(requests) == 1


@pytest.mark.parametrize("exception", [httpx.ConnectError, httpx.ReadTimeout, httpx.ConnectTimeout])
def test_chat_network_errors_do_not_retry_posts(exception):
    requests = []

    def handler(request):
        requests.append(request)
        raise exception("private network details", request=request)

    with AssistantClient(transport=httpx.MockTransport(handler)) as client:
        result = client.ask("question", "session")
    assert not result.ok and "try again" in result.error
    assert "private network details" not in result.error and len(requests) == 1


@pytest.mark.parametrize(
    "body",
    [
        "not json",
        "null",
        "[]",
        "{}",
        json.dumps(OK | {"sources": ["bad"]}),
        json.dumps(OK | {"escalate": "false"}),
        json.dumps(OK | {"confidence": float("nan")}),
        json.dumps(OK | {"request_id": ""}),
    ],
)
def test_malformed_success_is_a_recoverable_error(body):
    with AssistantClient(transport=httpx.MockTransport(lambda request: httpx.Response(200, text=body))) as client:
        result = client.ask("question", "session")
    assert not result.ok and "unreadable reply" in result.error


def test_nullable_legacy_fields_and_empty_sources_are_accepted():
    payload = OK | {"path": None, "confidence": None, "sources": []}
    with AssistantClient(transport=httpx.MockTransport(lambda request: httpx.Response(200, json=payload))) as client:
        result = client.ask("question", "session")
    assert result.ok and result.sources == [] and result.path == "" and result.confidence is None


@pytest.mark.parametrize("status", [200, 404, 500])
def test_health_status_is_bounded_and_explained(status):
    requests = []

    def handler(request):
        requests.append(request)
        return httpx.Response(status)

    with AssistantClient(timeout_s=10, transport=httpx.MockTransport(handler)) as client:
        assert client.healthy() is (status == 200)
        assert bool(client.health_error) is (status != 200)
    assert requests[0].url.path == "/health" and requests[0].method == "GET"
    assert requests[0].extensions["timeout"]["read"] == 2.0


@pytest.mark.parametrize("exception", [httpx.ConnectError, httpx.ReadTimeout])
def test_health_handles_unreachable_and_timeout(exception):
    def handler(request):
        raise exception("private error", request=request)

    with AssistantClient(transport=httpx.MockTransport(handler)) as client:
        assert not client.healthy()
        assert "conversation is kept" in client.health_error and "private error" not in client.health_error


@pytest.mark.parametrize("rating", [1, -1])
def test_feedback_201_uses_exact_request_id_and_rating(rating):
    requests = []

    def handler(request):
        requests.append(request)
        return httpx.Response(201, json={})

    with AssistantClient(transport=httpx.MockTransport(handler)) as client:
        assert client.send_feedback("request-1", rating, "Useful context")
        assert client.last_feedback_error == ""
    assert len(requests) == 1 and requests[0].url.path == "/v1/feedback"
    assert json.loads(requests[0].content) == {"request_id": "request-1", "rating": rating, "comment": "Useful context"}


@pytest.mark.parametrize(
    ("status", "message"),
    [(404, "ask the question again"), (422, "retry"), (429, "wait a minute"), (500, "try again"), (200, "try again")],
)
def test_feedback_requires_201_and_allows_retry(status, message):
    statuses = iter([status, 201])
    with AssistantClient(transport=httpx.MockTransport(lambda request: httpx.Response(next(statuses)))) as client:
        assert not client.send_feedback("request-1", -1)
        assert message in client.last_feedback_error
        assert client.send_feedback("request-1", -1) and client.last_feedback_error == ""


@pytest.mark.parametrize("exception", [httpx.ConnectError, httpx.ReadTimeout])
def test_feedback_network_failure_is_explained(exception):
    def handler(request):
        raise exception("private details", request=request)

    with AssistantClient(transport=httpx.MockTransport(handler)) as client:
        assert not client.send_feedback("request-1", -1)
        assert "try again" in client.last_feedback_error and "private details" not in client.last_feedback_error


@pytest.mark.parametrize("rating", [0, 2, True, "1"])
def test_invalid_feedback_rating_is_not_posted(rating):
    def unexpected(request):
        raise AssertionError("invalid feedback reached HTTP")

    with AssistantClient(transport=httpx.MockTransport(unexpected)) as client:
        assert not client.send_feedback("request-1", rating)
