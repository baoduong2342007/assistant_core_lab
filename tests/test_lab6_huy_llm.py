"""Huy's A2 and HTTP adapter tests; all providers use offline mock transports."""

import json

import httpx
import pytest

from assistant_core.config import Settings
from assistant_core.errors import ProviderError
from assistant_core.llm import OllamaLLM, OpenAICompatibleLLM, StubLLM, build_prompt, make_llm, parse_draft
from assistant_core.models import Intent, Message
from assistant_core.rag.answerer import ESCALATE_MSG, RagAnswerer
from assistant_core.rag.chunker import Chunk
from assistant_core.rag.index import Hit
from assistant_core.service import build_service


def raw_draft(**updates):
    return json.dumps({"answer": "Evidence.", "source_ids": ["H26#5.3"], "confidence": 0.8, "abstain": False} | updates)


@pytest.mark.parametrize("ids", [["H26#5.3"], ["H26#5.3", "S26#3"]])
def test_a2_accepts_only_retrieved_ids(ids):
    assert parse_draft(raw_draft(source_ids=ids), {"H26#5.3", "S26#3"}).source_ids == ids


@pytest.mark.parametrize("abstain", [False, True])
@pytest.mark.parametrize("ids", [["invented"], ["H26#5.3", "S26#3"]])
def test_a2_rejects_even_one_id_outside_this_turn(ids, abstain):
    with pytest.raises(ProviderError, match="not retrieved"):
        parse_draft(raw_draft(source_ids=ids, abstain=abstain), {"H26#5.3"})


@pytest.mark.parametrize(
    "raw",
    [
        "not json",
        "```json\n{}\n```",
        "[]",
        "null",
        "{}",
        raw_draft(source_ids=[]),
        raw_draft(answer="  "),
        raw_draft(answer=123),
        raw_draft(source_ids="H26#5.3"),
        raw_draft(source_ids=[123]),
        raw_draft(confidence=-0.1),
        raw_draft(confidence=1.1),
        raw_draft(confidence=float("nan")),
        raw_draft(confidence=float("inf")),
        raw_draft(confidence="0.8"),
        raw_draft(abstain="false"),
        raw_draft(abstain=0),
        raw_draft(unexpected="field"),
    ],
)
def test_a2_rejects_bad_json_or_schema(raw):
    with pytest.raises(ProviderError):
        parse_draft(raw, {"H26#5.3"})


@pytest.mark.parametrize("include_ids", [False, True])
def test_a2_abstention_allows_absent_or_empty_citations(include_ids):
    draft = {"answer": "", "confidence": 0.0, "abstain": True}
    if include_ids:
        draft["source_ids"] = []
    assert parse_draft(json.dumps(draft), {"H26#5.3"}).abstain


def test_a2_error_does_not_echo_provider_text():
    with pytest.raises(ProviderError) as error:
        parse_draft(raw_draft(answer={"private": "private-provider-payload"}), set())
    assert "private-provider-payload" not in str(error.value)


def test_prompt_preserves_literal_placeholders_in_input():
    chunk = Chunk("H26#5.3", "H26", "Title", "Evidence with {question}.", "1", "Office")
    prompt = build_prompt("Question with {sources}", [Hit(chunk, 3)])
    assert "[H26#5.3] Title: Evidence with {question}." in prompt
    assert "QUESTION: Question with {sources}" in prompt
    with pytest.raises(ProviderError, match="prompt version"):
        build_prompt("question", [], "../../private")


def mock_llm(kind, handler):
    transport = httpx.MockTransport(handler)
    if kind == "ollama":
        return OllamaLLM("demo", "http://localhost:11434/", 1.25, transport=transport)
    return OpenAICompatibleLLM("synthetic-key", "demo", "https://provider.test/v1/", 1.25, transport=transport)


def envelope(kind, raw):
    return {"message": {"content": raw}} if kind == "ollama" else {"choices": [{"message": {"content": raw}}]}


@pytest.mark.parametrize("kind", ["ollama", "openai"])
def test_adapter_request_contract_and_valid_draft(kind):
    requests = []

    def handler(request):
        requests.append(request)
        return httpx.Response(200, json=envelope(kind, raw_draft()))

    llm = mock_llm(kind, handler)
    try:
        draft = parse_draft(llm.complete("sample prompt"), {"H26#5.3"})
    finally:
        llm.close()
    assert draft.answer == "Evidence." and len(requests) == 1
    request = requests[0]
    body = json.loads(request.content)
    assert request.method == "POST"
    assert body["model"] == "demo" and body["messages"] == [{"role": "user", "content": "sample prompt"}]
    assert request.extensions["timeout"]["read"] == 1.25
    if kind == "ollama":
        assert str(request.url) == "http://localhost:11434/api/chat"
        assert body["stream"] is False and body["format"] == "json"
        assert body["options"]["temperature"] == 0
    else:
        assert str(request.url) == "https://provider.test/v1/chat/completions"
        assert request.headers["Authorization"] == "Bearer synthetic-key"
        assert body["temperature"] == 0 and body["response_format"] == {"type": "json_object"}


@pytest.mark.parametrize("kind", ["ollama", "openai"])
@pytest.mark.parametrize(
    "failure", ["timeout", "connection", "http", "json", "null", "list", "missing", "content", "empty_choices"]
)
def test_adapter_failures_retry_then_fall_back_without_leaking_body(kind, failure, caplog):
    requests = []

    def handler(request):
        requests.append(request)
        if failure == "timeout":
            raise httpx.ReadTimeout("private-provider-body", request=request)
        if failure == "connection":
            raise httpx.ConnectError("private-provider-body", request=request)
        if failure == "http":
            return httpx.Response(503, text="private-provider-body")
        if failure == "json":
            return httpx.Response(200, text="private-provider-body")
        payload = {
            "null": None,
            "list": [],
            "missing": {},
            "content": envelope(kind, None),
            "empty_choices": {"choices": []},
        }[failure]
        return httpx.Response(200, json=payload)

    llm = mock_llm(kind, handler)
    chunk = Chunk("H26#5.3", "H26", "Title", "Evidence.", "1", "Office")

    class Index:
        def search(self, query, k=3):
            return [Hit(chunk, 2.0)]

    try:
        result = RagAnswerer(Index(), llm).answer("policy question")
    finally:
        llm.close()
    assert len(requests) == 2
    assert result.path == "retrieval" and result.degraded
    assert [source.id for source in result.sources] == [chunk.id]
    assert "private-provider-body" not in result.answer + caplog.text


@pytest.mark.parametrize("kind", ["ollama", "openai"])
@pytest.mark.parametrize("first_reply", ["not json", raw_draft(source_ids=["H26#5.3", "unknown"])])
def test_invalid_draft_is_retried_and_valid_second_draft_is_used(kind, first_reply):
    replies = iter([first_reply, raw_draft()])
    llm = mock_llm(kind, lambda request: httpx.Response(200, json=envelope(kind, next(replies))))
    chunk = Chunk("H26#5.3", "H26", "Title", "Evidence.", "1", "Office")

    class Index:
        calls = 0

        def search(self, query, k=3):
            self.calls += 1
            return [Hit(chunk, 2.0)]

    index = Index()
    try:
        result = RagAnswerer(index, llm).answer("policy question")
    finally:
        llm.close()
    assert index.calls == 1
    assert result.path == "llm" and not result.degraded
    assert result.answer == "Evidence."


def test_model_abstention_returns_escalation_without_using_draft_text():
    class LLM:
        calls = 0

        def complete(self, prompt):
            self.calls += 1
            return raw_draft(answer="untrusted refusal text", abstain=True, source_ids=[], confidence=0.0)

    class Index:
        def search(self, query, k=3):
            return [Hit(Chunk("H26#5.3", "H26", "Title", "Evidence.", "1", "Office"), 3.0)]

    llm = LLM()
    result = RagAnswerer(Index(), llm).answer("question")
    assert llm.calls == 1
    assert result.answer == ESCALATE_MSG and result.path == "abstain"
    assert result.intent is Intent.UNKNOWN and result.escalate and result.sources == []


@pytest.mark.parametrize("kind", ["ollama", "openai"])
def test_service_factory_uses_selected_adapter_and_settings(monkeypatch, project_root, kind):
    calls = []

    class Provider:
        name = kind

        def complete(self, prompt):
            return raw_draft(source_ids=["S26#3"])

    provider = Provider()

    def factory(*args):
        calls.append(args)
        return provider

    monkeypatch.setattr("assistant_core.service.make_llm", factory)
    settings = Settings(
        data_dir=project_root / "data",
        llm_provider=kind,
        llm_model="demo",
        llm_base_url="https://provider.test/v1",
        llm_api_key="synthetic-key",
        llm_timeout_s=2.5,
    )
    service = build_service(settings)
    result = service.handle(Message(text="I lost my student card"))
    assert calls == [(kind, "demo", "https://provider.test/v1", "synthetic-key", 2.5)]
    assert service.rag.llm is provider and result.path == "llm"


def test_stub_and_fail_provider_stay_offline(monkeypatch, project_root):
    def unexpected_client(*args, **kwargs):
        raise AssertionError("offline path created HTTP client")

    monkeypatch.setattr("assistant_core.llm.httpx.Client", unexpected_client)
    assert isinstance(make_llm("stub", "demo", None, None, 1), StubLLM)
    service = build_service(Settings(data_dir=project_root / "data", llm_provider="ollama"), fail_provider=True)
    response = service.handle(Message(text="I lost my student card"))
    assert response.path == "retrieval" and response.degraded


@pytest.mark.parametrize("key", [None, "", " "])
def test_make_llm_rejects_missing_openai_key(key):
    with pytest.raises(ProviderError, match="LLM_API_KEY required"):
        make_llm("openai", "demo", None, key, 1)


@pytest.mark.parametrize("injected_service", [False, True])
def test_api_closes_only_the_provider_it_owns(monkeypatch, project_root, injected_service):
    from fastapi.testclient import TestClient

    from assistant_api.main import create_app

    class Provider:
        closed = False

        def close(self):
            self.closed = True

    provider = Provider()
    monkeypatch.setattr("assistant_core.service.make_llm", lambda *args: provider)
    settings = Settings(data_dir=project_root / "data", llm_provider="ollama")
    service = build_service(settings) if injected_service else None
    with TestClient(create_app(settings=settings, service=service)) as client:
        assert client.get("/health").status_code == 200
        assert not provider.closed
    assert provider.closed is not injected_service
    if service is not None:
        service.close()
        assert provider.closed
