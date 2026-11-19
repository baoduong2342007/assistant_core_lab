import json

import pytest
from fastapi.testclient import TestClient

from assistant_api.main import create_app
from assistant_core.config import Settings
from assistant_core.errors import ProviderError
from assistant_core.llm import parse_draft
from assistant_core.rag.answerer import RagAnswerer
from assistant_core.rag.chunker import Chunk
from assistant_core.rag.index import Hit


class Index:
    def __init__(self, hits):
        self.hits = hits
        self.calls = 0

    def search(self, query, k=3):
        self.calls += 1
        return self.hits


class Provider:
    def __init__(self, raw):
        self.raw = raw
        self.calls = 0

    def complete(self, prompt):
        self.calls += 1
        return self.raw


def test_threshold_and_fallback():
    chunk = Chunk("H#1", "H", "Title", "Evidence.", "1", "Office")
    provider = Provider("invalid")
    for hits in ([], [Hit(chunk, 1.99)]):
        result = RagAnswerer(Index(hits), provider, 2).answer("question")
        assert result.path == "abstain" and result.escalate and result.confidence == 0
    assert provider.calls == 0
    result = RagAnswerer(Index([Hit(chunk, 2)]), provider, 2).answer("question")
    assert provider.calls == 2 and result.degraded and result.sources[0].id == "H#1"


def test_citation_validation():
    def raw(ids, abstain=False):
        return json.dumps({"answer": "answer", "source_ids": ids, "confidence": 0.8, "abstain": abstain})

    assert parse_draft(raw(["H#1"]), {"H#1"}).source_ids == ["H#1"]
    assert parse_draft(raw([], True), {"H#1"}).abstain
    for bad in (raw([]), raw(["H#1", "fake"]), "not json"):
        with pytest.raises(ProviderError):
            parse_draft(bad, {"H#1"})


@pytest.mark.parametrize(
    ("question", "source", "expected"),
    [
        ("student card replacement fee", "S26#3", "50,000 VND"),
        ("how long can I keep a library book", "S26#1", "14 days"),
        ("when is tuition due", "F26#3", "end of week 6"),
        ("can I take 32 credits", "H26#6.1", "requires approval"),
    ],
)
def test_policy_questions_use_sources(project_root, question, source, expected):
    with TestClient(create_app(Settings(data_dir=project_root / "data"))) as client:
        response = client.post("/v1/chat", json={"message": question})
    assert response.status_code == 200
    body = response.json()
    assert body["path"] == "llm"
    assert body["sources"][0]["id"] == source
    assert expected in body["answer"]


@pytest.mark.parametrize(
    "question",
    [
        "Is a calculator allowed during the final exam?",
        "Are smart watches allowed during the final exam?",
        "Can I borrow a laptop from the library?",
    ],
)
def test_specific_policy_without_evidence_abstains(project_root, question):
    with TestClient(create_app(Settings(data_dir=project_root / "data"))) as client:
        response = client.post("/v1/chat", json={"message": question})
    assert response.status_code == 200
    body = response.json()
    assert body["path"] == "abstain" and body["escalate"]
    assert body["sources"] == []


def test_exam_format_requires_support_from_the_chunk():
    absence = Chunk("H#1", "H", "Exam absence", "Submit a medical certificate.", "1", "Office")
    format_rule = Chunk("H#2", "H", "Final exam format", "The final exam is open book.", "1", "Office")
    provider = Provider("invalid")
    question = "is the final exam open-book?"
    response = RagAnswerer(Index([Hit(absence, 5)]), provider).answer(question)
    assert response.path == "abstain" and response.escalate
    assert response.sources == [] and provider.calls == 0

    response = RagAnswerer(Index([Hit(absence, 5), Hit(format_rule, 3)]), None).answer(question)
    assert response.path == "retrieval" and response.sources[0].id == "H#2"


def test_api_rag_feedback_restart(tmp_path, project_root):
    settings = Settings(
        data_dir=project_root / "data", database_url=f'sqlite:///{tmp_path / "chat.db"}', api_admin_key="test-key"
    )
    with TestClient(create_app(settings)) as client:
        fee = client.post("/v1/chat", json={"message": "tuition for 18 credits and 2 retake"}).json()
        assert "9,450,000" in fee["answer"] and fee["path"] == "deterministic"
        card = client.post("/v1/chat", json={"message": "I lost my student card"}).json()
        assert card["path"] == "llm" and card["sources"][0]["id"] == "S26#3"
        no_source = client.post("/v1/chat", json={"message": "what is the capital of France"}).json()
        assert no_source["path"] == "abstain" and no_source["escalate"]
        private = client.post("/v1/chat", json={"message": "tuition and my friend's GPA"}).json()
        assert private["path"] == "abstain" and not private["escalate"]
        assert client.post("/v1/feedback", json={"request_id": card["request_id"], "rating": 1}).status_code == 201
    with TestClient(create_app(settings)) as client:
        feedback = client.get("/v1/feedback", headers={"X-Admin-Key": "test-key"}).json()
        assert any(item["request_id"] == card["request_id"] for item in feedback)
