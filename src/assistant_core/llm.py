"""Structured Lab 06 answers and an offline provider for evaluation."""

import json
import re
from pathlib import Path
from typing import Protocol

from pydantic import BaseModel, Field, ValidationError

from assistant_core.errors import ProviderError
from assistant_core.rag.index import Hit

PROMPTS = Path(__file__).parent / "prompts"


class AnswerDraft(BaseModel):
    answer: str = Field(max_length=800)
    source_ids: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0, le=1)
    abstain: bool = False


class LLM(Protocol):
    def complete(self, prompt: str) -> str: ...


def build_prompt(question: str, hits: list[Hit], version: str = "answer_v1") -> str:
    template = (PROMPTS / f"{version}.txt").read_text(encoding="utf-8")
    sources = "\n".join(f"[{hit.chunk.id}] {hit.chunk.title}: {hit.chunk.text}" for hit in hits)
    return template.replace("{sources}", sources).replace("{question}", question)


def parse_draft(raw: str, allowed_ids: set[str]) -> AnswerDraft:
    """Require a structured draft whose cited IDs were retrieved for this question."""
    try:
        draft = AnswerDraft.model_validate_json(raw, strict=True)
    except ValidationError as exc:
        raise ProviderError("invalid structured output") from exc

    if set(draft.source_ids) - allowed_ids:
        raise ProviderError("answer cites sources that were not retrieved")
    if not draft.abstain and (not draft.answer.strip() or not draft.source_ids):
        raise ProviderError("answer is missing text or citations")
    return draft


class StubLLM:
    """Quote the first sentence of the first source deterministically."""

    name = "stub"

    def __init__(self, fail: bool = False, garbage: bool = False):
        self.fail = fail
        self.garbage = garbage

    def complete(self, prompt: str) -> str:
        if self.fail:
            raise ProviderError("stub provider unavailable")
        if self.garbage:
            return "This output contains no JSON."
        source = re.search(r"^\[([^\]]+)\] ([^:]+): (.+)$", prompt, flags=re.M)
        if source is None:
            return json.dumps({"answer": "", "source_ids": [], "confidence": 0.0, "abstain": True})
        source_id, title, text = source.groups()
        first_sentence = re.split(r"(?<=\.)\s", text, maxsplit=1)[0]
        return json.dumps(
            {
                "answer": f"According to {title}: {first_sentence}",
                "source_ids": [source_id],
                "confidence": 0.7,
                "abstain": False,
            }
        )
