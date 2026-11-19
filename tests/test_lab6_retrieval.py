import json
from unittest.mock import Mock

import pytest

from assistant_core.errors import DataError, ProviderError
from assistant_core.llm import StubLLM, parse_draft
from assistant_core.models import Intent, Message
from assistant_core.rag.answerer import RagAnswerer
from assistant_core.rag.chunker import load_folder
from assistant_core.rag.index import Hit, make_index
from assistant_core.responder import TemplateResponder
from assistant_core.service import AssistantService

THESIS_QUERY = "can I register my thesis with 118 credits"
OUT_OF_SCOPE_QUERY = "what is the capital of France"


@pytest.fixture
def chunks(project_root):
    return load_folder(project_root / "data" / "kb")


def test_kb_chunk_ids_and_metadata(chunks):
    expected = {
        "F26": ({"1", "2", "3", "4"}, "Finance Office"),
        "H26": ({"4.2", "5.3", "5.4", "6.1", "7.2", "8.1", "8.3"}, "Training Office"),
        "S26": ({"1", "2", "3"}, "Student Affairs"),
    }
    assert len(chunks) == 14
    assert {chunk.id for chunk in chunks} == {
        f"{doc_id}#{section}" for doc_id, (sections, _) in expected.items() for section in sections
    }
    for chunk in chunks:
        assert chunk.version == "2026.1"
        assert chunk.owner == expected[chunk.doc_id][1]
        assert chunk.title and chunk.text


def test_duplicate_chunk_id_fails_loading(tmp_path):
    for name in ("a.md", "b.md"):
        (tmp_path / name).write_text("---\ndoc_id: H26\n---\n# 5.3 Thesis\nExample text.\n", encoding="utf-8")
    with pytest.raises(DataError, match=r"Duplicate chunk ID H26#5\.3 in b\.md"):
        load_folder(tmp_path)


@pytest.mark.parametrize("kind", ["bm25", "tfidf", "hybrid"])
def test_indexes_find_thesis_and_skip_unmatched_queries(chunks, kind):
    index = make_index(kind, chunks)
    hits = index.search(THESIS_QUERY, k=1)
    assert len(hits) == 1
    assert hits[0].chunk.id == "H26#5.3"
    assert hits[0].score > 0
    assert index.search(OUT_OF_SCOPE_QUERY) == []


def test_bm25_preserves_baseline_score(chunks):
    hits = make_index("bm25", chunks).search(THESIS_QUERY)
    assert hits[0].score == pytest.approx(4.914)
    assert [hit.score for hit in hits] == sorted((hit.score for hit in hits), reverse=True)


@pytest.mark.parametrize("score", [None, 1.999])
def test_a1_abstains_without_calling_provider(chunks, score):
    index = Mock()
    index.search.return_value = [] if score is None else [Hit(chunks[0], score)]
    provider = Mock()
    response = RagAnswerer(index, provider).answer(THESIS_QUERY)
    assert response.path == "abstain"
    assert response.intent is Intent.UNKNOWN
    assert response.escalate and response.confidence == 0.0
    assert response.sources == []
    index.search.assert_called_once_with(THESIS_QUERY, 3)
    provider.complete.assert_not_called()


def test_a1_accepts_score_at_threshold(chunks):
    index = Mock()
    index.search.return_value = [Hit(chunks[0], 2.0)]
    provider = Mock(wraps=StubLLM())
    response = RagAnswerer(index, provider).answer("What is tuition per credit?")
    assert response.path == "llm" and response.sources[0].id == chunks[0].id
    provider.complete.assert_called_once()


@pytest.mark.parametrize(
    "raw",
    [
        "invalid JSON",
        '{"answer": "Example", "source_ids": ["F26#2"], "confidence": "0.8"}',
        '{"answer": "Example", "source_ids": ["F26#2"], "confidence": 1.5}',
        '{"answer": "Example", "source_ids": [], "confidence": 0.8}',
        '{"answer": "Example", "source_ids": ["F26#2", "H26#5.3"], "confidence": 0.8}',
        '{"answer": "", "source_ids": ["H26#5.3"], "confidence": 0.0, "abstain": true}',
    ],
)
def test_a2_rejects_invalid_drafts(raw):
    with pytest.raises(ProviderError):
        parse_draft(raw, {"F26#2"})


def test_a2_accepts_grounded_draft_and_source_free_abstention():
    grounded = json.dumps({"answer": "1.5 times the regular rate", "source_ids": ["F26#2"], "confidence": 0.8})
    assert parse_draft(grounded, {"F26#2"}).source_ids == ["F26#2"]
    assert parse_draft('{"answer": "", "confidence": 0, "abstain": true}', {"F26#2"}).abstain


@pytest.mark.parametrize("stub", [StubLLM(garbage=True), StubLLM(fail=True)])
def test_rag_falls_back_to_top_chunk_after_two_failures(chunks, stub):
    provider = Mock(wraps=stub)
    response = RagAnswerer(make_index("bm25", chunks), provider).answer(THESIS_QUERY)
    assert response.path == "retrieval" and response.degraded
    assert [source.id for source in response.sources] == ["H26#5.3"]
    assert provider.complete.call_count == 2


def test_service_routes_tools_and_refuses_private_requests_before_search(
    sample_settings, sample_offices, sample_handbook
):
    index = Mock()
    rag = RagAnswerer(index, StubLLM())
    service = AssistantService(sample_settings, sample_offices, sample_handbook, TemplateResponder(), rag)
    assert "9,450,000" in service.handle(Message(text="tuition for 18 credits and 2 retake")).answer
    assert "B.201" in service.handle(Message(text="where is the library")).answer
    response = service.handle(Message(text="what tuition grade did my friend get"))
    assert response.path == "abstain" and not response.escalate
    index.search.assert_not_called()
