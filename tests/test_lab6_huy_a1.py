"""Personal acceptance of A1 with explicit retrieval/provider call counts."""

import json

import pytest

from assistant_core.models import Intent
from assistant_core.rag.answerer import RagAnswerer
from assistant_core.rag.chunker import Chunk
from assistant_core.rag.index import Hit


@pytest.mark.parametrize("score", [None, 1.999, 2.0])
def test_a1_blocks_model_until_evidence_meets_threshold(score):
    chunk = Chunk("H26#5.3", "H26", "Thesis", "At least 120 credits.", "2026.1", "Training Office")

    class Index:
        calls = 0

        def search(self, query, k=3):
            self.calls += 1
            return [] if score is None else [Hit(chunk, score)]

    class Provider:
        calls = 0

        def complete(self, prompt):
            self.calls += 1
            return json.dumps({"answer": chunk.text, "source_ids": [chunk.id], "confidence": 0.7})

    index, provider = Index(), Provider()
    result = RagAnswerer(index, provider, min_score=2.0).answer("thesis requirements")
    assert index.calls == 1
    if score == 2.0:
        assert provider.calls == 1 and result.path == "llm"
        assert result.sources[0].id == chunk.id
    else:
        assert provider.calls == 0 and result.path == "abstain"
        assert result.intent is Intent.UNKNOWN and result.escalate
        assert result.confidence == 0.0 and result.sources == []
