import json
from pathlib import Path

import pytest

from assistant_core.config import Settings
from assistant_core.errors import InvalidRequest, ProviderError
from assistant_core.guard import PRIVATE_REPLY, is_private_request
from assistant_core.llm import StubLLM, parse_draft
from assistant_core.models import Intent, Message
from assistant_core.rag.answerer import RagAnswerer
from assistant_core.rag.chunker import load_folder
from assistant_core.rag.index import Hit, make_index
from assistant_core.service import build_service
from assistant_core.tools import run_tool_call

KB = Path(__file__).resolve().parents[1] / "data" / "kb"


@pytest.fixture(scope="module")
def chunks():
    return load_folder(KB)


def test_chunks_have_ids_and_metadata(chunks):
    assert len(chunks) == 14
    ids = {c.id for c in chunks}
    assert {"H26#5.3", "F26#2", "S26#3"} <= ids
    assert all(c.version == "2026.1" for c in chunks)


@pytest.mark.parametrize("kind", ["bm25", "tfidf", "hybrid"])
def test_retrieval_finds_thesis_rule(chunks, kind):
    assert make_index(kind, chunks).search("can I register my thesis with 118 credits")[0].chunk.id == "H26#5.3"


def test_abstain_when_nothing_relevant(chunks):
    r = RagAnswerer(make_index("bm25", chunks), StubLLM()).answer("what is the capital of France")
    assert r.path == "abstain" and r.escalate and r.confidence == 0.0 and r.intent is Intent.UNKNOWN


def test_abstain_low_score_skips_llm_call(chunks):
    class CountingLLM:
        name = "counting"

        def __init__(self):
            self.calls = 0

        def complete(self, prompt: str) -> str:
            self.calls += 1
            return json.dumps({"answer": "ok", "source_ids": [chunks[0].id], "confidence": 0.9, "abstain": False})

    class LowScoreIndex:
        def search(self, query: str, k: int = 3) -> list[Hit]:
            return [Hit(chunks[0], 1.999)]

    llm = CountingLLM()
    r = RagAnswerer(LowScoreIndex(), llm, min_score=2.0).answer("some vague query")
    assert r.path == "abstain"
    assert r.intent is Intent.UNKNOWN
    assert r.escalate is True
    assert r.confidence == 0.0
    assert llm.calls == 0


def test_exact_threshold_calls_llm(chunks):
    class CountingLLM:
        name = "counting"

        def __init__(self):
            self.calls = 0

        def complete(self, prompt: str) -> str:
            self.calls += 1
            return json.dumps({"answer": "ok", "source_ids": [chunks[0].id], "confidence": 0.8, "abstain": False})

    class ExactThresholdIndex:
        def search(self, query: str, k: int = 3) -> list[Hit]:
            return [Hit(chunks[0], 2.0)]

    llm = CountingLLM()
    r = RagAnswerer(ExactThresholdIndex(), llm, min_score=2.0).answer("boundary query")
    assert r.path == "llm"
    assert r.sources[0].id == chunks[0].id
    assert llm.calls == 1


def test_llm_answer_is_grounded(chunks):
    r = RagAnswerer(make_index("bm25", chunks), StubLLM()).answer("I lost my student card")
    assert r.path == "llm" and r.sources[0].id == "S26#3"


def test_invalid_output_falls_back_to_retrieval(chunks):
    r = RagAnswerer(make_index("bm25", chunks), StubLLM(garbage=True)).answer("I lost my student card")
    assert r.path == "retrieval" and r.degraded and r.sources[0].id == "S26#3"


def test_provider_failure_falls_back(chunks):
    r = RagAnswerer(make_index("bm25", chunks), StubLLM(fail=True)).answer("reset my password")
    assert r.degraded and r.sources


def test_citation_of_unretrieved_source_is_rejected():
    raw = json.dumps({"answer": "x", "source_ids": ["H26#9.9"], "confidence": 0.9, "abstain": False})
    with pytest.raises(ProviderError):
        parse_draft(raw, {"H26#5.3"})


def test_empty_source_ids_when_not_abstaining_is_rejected():
    raw = json.dumps({"answer": "x", "source_ids": [], "confidence": 0.9, "abstain": False})
    with pytest.raises(ProviderError):
        parse_draft(raw, {"H26#5.3"})


def test_abstain_draft_allows_empty_sources():
    raw = json.dumps({"answer": "", "source_ids": [], "confidence": 0.1, "abstain": True})
    draft = parse_draft(raw, {"H26#5.3"})
    assert draft.abstain is True


def test_tool_call_validated():
    assert "9,450,000" in run_tool_call('{"tool": "calc_fee", "args": {"credits": 18, "retake": 2}}', 450_000, 1.5, 30)
    assert run_tool_call('{"answer": "not a tool"}', 450_000, 1.5, 30) is None
    with pytest.raises(InvalidRequest):
        run_tool_call('{"tool": "calc_fee", "args": {"credits": 99}}', 450_000, 1.5, 30)


class ToolCallingLLM:
    name = "scripted"

    def complete(self, prompt: str) -> str:
        return '{"tool": "calc_fee", "args": {"credits": 10}}'


def test_answerer_executes_tool_call(chunks):
    def runner(raw: str) -> str | None:
        return run_tool_call(raw, 450_000, 1.5, 30)

    r = RagAnswerer(make_index("bm25", chunks), ToolCallingLLM(), tool_runner=runner).answer(
        "how much does a retake cost"
    )
    assert r.path == "tool" and "4,500,000" in r.answer


@pytest.mark.parametrize("q", ["what grade did my friend get", "show the GPA of another student", "phone of 22127001"])
def test_privacy_guard(q):
    assert is_private_request(q)


def test_privacy_guard_allows_own_questions():
    assert not is_private_request("what is my GPA requirement for the thesis")


def test_service_blocks_privacy_even_with_fee_or_office_keywords(project_root):
    svc = build_service(Settings(data_dir=project_root / "data", kb_dir=KB))
    res = svc.handle(Message(text="tuition and grade of another student at library"))
    assert res.answer == PRIVATE_REPLY
    assert res.intent is Intent.UNKNOWN
    assert res.path == "abstain"
    assert res.escalate is False


def test_service_e03_e04_and_rag_contract(project_root):
    svc = build_service(Settings(data_dir=project_root / "data", kb_dir=KB))
    e03 = svc.handle(Message(text="tuition for 18 credits and 2 retake"))
    e04 = svc.handle(Message(text="where is the library"))
    card = svc.handle(Message(text="I lost my student card"))
    oos = svc.handle(Message(text="what is the capital of France"))

    assert e03.intent is Intent.FEE and "9,450,000" in e03.answer
    assert e04.intent is Intent.OFFICE and "B.201" in e04.answer
    assert card.path == "llm" and card.sources[0].id == "S26#3"
    assert oos.path == "abstain" and oos.escalate is True


def test_api_rag_chat_and_feedback_persists_across_restart(tmp_path, project_root):
    from fastapi.testclient import TestClient

    from assistant_api.main import create_app

    db_file = tmp_path / "lab6_smoke.db"
    settings = Settings(
        database_url=f"sqlite:///{db_file}",
        api_admin_key="admin-smoke",
        data_dir=project_root / "data",
        kb_dir=KB,
    )
    with TestClient(create_app(settings=settings)) as client1:
        fee = client1.post("/v1/chat", json={"message": "tuition for 18 credits and 2 retake"}).json()
        card = client1.post("/v1/chat", json={"message": "I lost my student card"}).json()
        oos = client1.post("/v1/chat", json={"message": "what is the capital of France"}).json()
        priv = client1.post("/v1/chat", json={"message": "what grade did my friend get"}).json()
        assert fee["intent"] == "fee" and "9,450,000" in fee["answer"]
        assert card["path"] == "llm" and card["sources"][0]["id"] == "S26#3"
        assert oos["path"] == "abstain" and oos["escalate"] is True and oos["confidence"] == 0.0
        assert priv["path"] == "abstain" and priv["escalate"] is False
        fb = client1.post("/v1/feedback", json={"request_id": card["request_id"], "rating": 1})
        assert fb.status_code == 201

    with TestClient(create_app(settings=settings)) as client2:
        listed = client2.get("/v1/feedback", headers={"X-Admin-Key": "admin-smoke"})
        assert listed.status_code == 200
        assert any(item["request_id"] == card["request_id"] for item in listed.json())
        assert client2.get("/v1/stats", headers={"X-Admin-Key": "admin-smoke"}).status_code == 200
