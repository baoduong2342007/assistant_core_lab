"""Comprehensive test suite for Bảo (simble2k):
- A1: Zero LLM provider calls when no hits or score < min_score; LLM called when score >= min_score.
- Guard: Privacy / PII blocked before retrieval with escalate=False, allowing valid policy GPA queries.
- Fallback: Fallback to top-hit retrieval with degraded=True after retries exhausted (error or invalid citations).
- Regression: FastAPI chat -> feedback -> app restart with same SQLite file -> feedback retrieved.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from assistant_api.main import create_app
from assistant_core.config import Settings
from assistant_core.errors import ProviderError
from assistant_core.guard import PRIVATE_REPLY, is_private_request
from assistant_core.knowledge import Handbook, OfficeDirectory
from assistant_core.models import Intent, Message
from assistant_core.rag.answerer import RagAnswerer
from assistant_core.rag.chunker import Chunk, load_folder
from assistant_core.rag.index import Hit, Index, make_index
from assistant_core.responder import StubLLMResponder
from assistant_core.service import AssistantService


class CountingLLM:
    """Mock LLM tracking the number of calls to complete()."""

    name = "counting_mock"

    def __init__(self, answer: str = "Test answer", source_ids: list[str] | None = None):
        self.call_count = 0
        self.answer = answer
        self.source_ids = source_ids

    def complete(self, prompt: str) -> str:
        self.call_count += 1
        ids = self.source_ids if self.source_ids is not None else ["H26#5.3"]
        return json.dumps(
            {
                "answer": self.answer,
                "source_ids": ids,
                "confidence": 0.85,
                "abstain": False,
            }
        )


class FailingLLM:
    """Mock LLM that always raises ProviderError."""

    name = "failing_mock"

    def __init__(self):
        self.call_count = 0

    def complete(self, prompt: str) -> str:
        self.call_count += 1
        raise ProviderError("Upstream LLM provider connection timed out")


class HallucinatingLLM:
    """Mock LLM returning citation IDs not present in retrieved chunks."""

    name = "hallucinating_mock"

    def __init__(self):
        self.call_count = 0

    def complete(self, prompt: str) -> str:
        self.call_count += 1
        return json.dumps(
            {
                "answer": "Hallucinated policy answer",
                "source_ids": ["NON_EXISTENT_ID#99.9"],
                "confidence": 0.99,
                "abstain": False,
            }
        )


@pytest.fixture
def test_kb_index(project_root: Path) -> Index:
    kb_path = project_root / "data" / "kb"
    chunks = load_folder(kb_path)
    return make_index("bm25", chunks)


# ==============================================================================
# 1. A1 Test Suite: Verification of Zero LLM Calls on No-Hit / Low-Score
# ==============================================================================


def test_a1_zero_llm_calls_when_no_hits(test_kb_index: Index):
    """When query yields no hits, A1 must return abstain with escalate=True and 0 LLM calls."""
    llm = CountingLLM()
    answerer = RagAnswerer(index=test_kb_index, llm=llm, min_score=2.0)

    # Out-of-scope query that produces zero hits in the campus KB
    resp = answerer.answer("what is the capital of France")

    assert resp.path == "abstain"
    assert resp.intent == Intent.UNKNOWN
    assert resp.escalate is True
    assert resp.confidence == 0.0
    assert llm.call_count == 0, f"Expected 0 LLM calls, but got {llm.call_count}"


def test_a1_zero_llm_calls_when_score_below_threshold():
    """When top hit score is below min_score, A1 must abstain without invoking LLM."""

    # Synthetic index with a single low-scoring hit
    class MockLowScoreIndex:
        def search(self, query: str, k: int = 3) -> list[Hit]:
            chunk = Chunk(
                id="H26#1.1",
                title="Low hit",
                text="irrelevant text",
                doc_id="H26",
                version="2026.1",
                owner="Training Office",
            )
            return [Hit(chunk=chunk, score=1.2)]

    llm = CountingLLM()
    answerer = RagAnswerer(index=MockLowScoreIndex(), llm=llm, min_score=2.0)

    resp = answerer.answer("some borderline query")

    assert resp.path == "abstain"
    assert resp.intent == Intent.UNKNOWN
    assert resp.escalate is True
    assert resp.confidence == 0.0
    assert llm.call_count == 0, f"Expected 0 LLM calls, but got {llm.call_count}"


def test_a1_calls_llm_when_score_meets_or_exceeds_threshold(test_kb_index: Index):
    """When score meets min_score, LLM is called and response is returned."""
    llm = CountingLLM(source_ids=["H26#5.3"])
    answerer = RagAnswerer(index=test_kb_index, llm=llm, min_score=2.0)

    resp = answerer.answer("thesis registration requirements 120 credits")

    assert llm.call_count >= 1
    assert resp.path == "llm"
    assert resp.intent == Intent.RULE
    assert resp.escalate is False
    assert len(resp.sources) == 1
    assert resp.sources[0].id == "H26#5.3"


# ==============================================================================
# 2. Guardrails Test Suite: Privacy / PII Interception
# ==============================================================================


@pytest.mark.parametrize(
    "private_query",
    [
        "what grade did my friend get in math",
        "tell me about my classmate's score",
        "can you show the gpa of another student",
        "what is the phone number of my roommate",
        "check score for student 20260001",
    ],
)
def test_guard_intercepts_private_requests(private_query: str):
    """Guard should detect private PII keywords and student IDs."""
    assert is_private_request(private_query) is True


def test_guard_service_blocks_pii_with_escalate_false(test_kb_index: Index, project_root: Path):
    """Private queries are rejected at Service.handle with escalate=False and no retrieval/LLM."""
    llm = CountingLLM()
    rag = RagAnswerer(index=test_kb_index, llm=llm, min_score=2.0)
    settings = Settings(data_dir=project_root / "data")
    offices = OfficeDirectory.from_csv(project_root / "data" / "offices.csv")
    handbook = Handbook.from_json(project_root / "data" / "handbook.json")
    service = AssistantService(settings, offices, handbook, StubLLMResponder(), rag=rag)

    resp = service.handle(Message(text="what grade did my friend get"))

    assert resp.path == "abstain"
    assert resp.escalate is False  # Privacy block is not an escalation
    assert resp.confidence == 0.0
    assert resp.answer == PRIVATE_REPLY
    assert llm.call_count == 0


def test_guard_allows_valid_policy_gpa_query(test_kb_index: Index, project_root: Path):
    """Queries asking about policy criteria containing GPA/credits must NOT be blocked."""
    assert is_private_request("can I register my thesis with 118 credits and cumulative GPA of 2.0") is False

    rag = RagAnswerer(index=test_kb_index, llm=CountingLLM(source_ids=["H26#5.3"]), min_score=2.0)
    settings = Settings(data_dir=project_root / "data")
    offices = OfficeDirectory.from_csv(project_root / "data" / "offices.csv")
    handbook = Handbook.from_json(project_root / "data" / "handbook.json")
    service = AssistantService(settings, offices, handbook, StubLLMResponder(), rag=rag)

    resp = service.handle(Message(text="can I register my thesis with 118 credits and GPA 2.0"))
    assert resp.path == "llm"
    assert resp.intent == Intent.RULE


# ==============================================================================
# 3. Fallback Test Suite: Retry and Degraded Fallback on Provider Failure
# ==============================================================================


def test_fallback_on_provider_error_after_retries(test_kb_index: Index):
    """When LLM provider fails repeatedly, fallback to retrieval-only with degraded=True."""
    failing_llm = FailingLLM()
    answerer = RagAnswerer(index=test_kb_index, llm=failing_llm, min_score=2.0, retries=1)

    resp = answerer.answer("how many credits for thesis registration")

    # Retries = 1 means 2 attempts total (attempt 0, attempt 1)
    assert failing_llm.call_count == 2
    assert resp.path == "retrieval"
    assert resp.degraded is True
    assert len(resp.sources) >= 1
    assert "5.3 Thesis registration" in resp.answer


def test_fallback_on_hallucinated_citations(test_kb_index: Index):
    """When LLM outputs invalid citations not in retrieved set, fallback to degraded retrieval."""
    hallucinating_llm = HallucinatingLLM()
    answerer = RagAnswerer(index=test_kb_index, llm=hallucinating_llm, min_score=2.0, retries=1)

    resp = answerer.answer("how many credits for thesis registration")

    assert hallucinating_llm.call_count == 2
    assert resp.path == "retrieval"
    assert resp.degraded is True
    assert len(resp.sources) >= 1


# ==============================================================================
# 4. Regression Test Suite: API + SQLite Persistence Across Restart
# ==============================================================================


def test_api_chat_feedback_sqlite_persistence_restart(tmp_path: Path, project_root: Path):
    """Smoke test: /v1/chat -> /v1/feedback -> restart app on same DB -> retrieve feedback."""
    db_file = tmp_path / "bao_test.db"
    db_url = f"sqlite:///{db_file}"
    admin_key = "secret-bao-key"

    settings = Settings(
        database_url=db_url,
        data_dir=project_root / "data",
        kb_dir=project_root / "data" / "kb",
        api_admin_key=admin_key,
        llm_provider="stub",
    )

    # 1. First run: Start app, perform chat and leave feedback
    app1 = create_app(settings)
    client1 = TestClient(app1)

    # Chat with RAG
    chat_resp = client1.post("/v1/chat", json={"message": "I lost my student card", "session_id": "test-session"})
    assert chat_resp.status_code == 200
    chat_data = chat_resp.json()
    request_id = chat_data["request_id"]
    assert chat_data["path"] == "llm"
    assert any(s["id"] == "S26#3" for s in chat_data["sources"])

    # Submit feedback
    fb_resp = client1.post(
        "/v1/feedback",
        json={"request_id": request_id, "rating": 1, "comment": "Accurate student card replacement info"},
    )
    assert fb_resp.status_code == 201
    fb_data = fb_resp.json()
    assert fb_data["request_id"] == request_id
    assert fb_data["rating"] == 1

    # 2. Simulate complete application restart using the SAME SQLite file
    app2 = create_app(settings)
    client2 = TestClient(app2)

    # Retrieve feedback using admin key
    list_resp = client2.get("/v1/feedback", headers={"X-Admin-Key": admin_key})
    assert list_resp.status_code == 200
    feedbacks = list_resp.json()
    assert len(feedbacks) >= 1
    target = next((item for item in feedbacks if item["request_id"] == request_id), None)
    assert target is not None
    assert target["rating"] == 1
    assert target["comment"] == "Accurate student card replacement info"
