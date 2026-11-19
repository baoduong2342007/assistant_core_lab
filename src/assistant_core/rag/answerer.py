"""Answer policy questions with retrieval + LLM, safely.

Order of defences:
  1. retrieve; if the best score is too low -> ABSTAIN and escalate (no LLM call)
  2. ask the LLM for structured JSON; validate schema + grounding; retry once
  3. on provider failure or invalid output -> quote the best source (retrieval-only fallback)
"""

from __future__ import annotations

import logging
import re
from collections.abc import Callable

from assistant_core.errors import InvalidRequest, ProviderError
from assistant_core.llm import LLM, AnswerDraft, build_prompt, parse_draft
from assistant_core.models import Intent, Response, Source
from assistant_core.rag.index import Index
from assistant_core.router import is_tuition_deadline

log = logging.getLogger("assistant_core.rag")
ESCALATE_MSG = (
    "I'm not confident I can answer that from the official documents. "
    "Please contact the Training Office (room I.101) or ask your academic advisor."
)


_CREDIT_LOAD = re.compile(
    r"\b(?:take|enroll in|register for)\s+(?:more than\s+)?\d+\s+credits?\b",
    re.IGNORECASE,
)
_BOOK_FORMAT = re.compile(r"\b(?:open|closed)[ -]book\b", re.IGNORECASE)


_EXAM = re.compile(r"\b(?:exams?|tests?|quizzes?)\b", re.IGNORECASE)
_LIBRARY_LOAN = re.compile(r"\b(?:library|borrow\w*|loans?)\b", re.IGNORECASE)
_EXAM_DEVICES = (
    re.compile(r"\bcalculators?\b", re.IGNORECASE),
    re.compile(r"\bsmart[ -]?watch(?:es)?\b", re.IGNORECASE),
)
_LIBRARY_DEVICES = (
    re.compile(r"\b(?:laptops?|notebooks?)\b", re.IGNORECASE),
    re.compile(r"\btablets?\b", re.IGNORECASE),
)


def _required_evidence(question: str) -> list[re.Pattern[str]]:
    """Identify explicit policy details that a merely related chunk cannot answer."""
    required = [_BOOK_FORMAT] if _BOOK_FORMAT.search(question) else []
    if _EXAM.search(question):
        required.extend(pattern for pattern in _EXAM_DEVICES if pattern.search(question))
    if _LIBRARY_LOAN.search(question):
        required.extend(pattern for pattern in _LIBRARY_DEVICES if pattern.search(question))
    return required


def _search_query(question: str) -> str:
    """Expand common paraphrases using the handbook's terminology."""
    if is_tuition_deadline(question):
        return f"{question} payment deadline"
    if _CREDIT_LOAD.search(question):
        return f"{question} credit load"
    return question


class RagAnswerer:
    def __init__(
        self,
        index: Index,
        llm: LLM | None,
        min_score: float = 2.0,
        k: int = 3,
        prompt_version: str = "answer_v1",
        retries: int = 1,
        tool_runner: Callable[[str], str | None] | None = None,
    ):
        self.index, self.llm, self.min_score, self.k = index, llm, min_score, k
        self.prompt_version, self.retries, self.tool_runner = prompt_version, retries, tool_runner

    def answer(self, question: str) -> Response:
        hits = self.index.search(_search_query(question), self.k)
        required = _required_evidence(question)
        if required:
            hits = [
                hit
                for hit in hits
                if all(pattern.search(f"{hit.chunk.title} {hit.chunk.text}") for pattern in required)
            ]
        if not hits or hits[0].score < self.min_score:
            return Response(answer=ESCALATE_MSG, intent=Intent.UNKNOWN, path="abstain", escalate=True, confidence=0.0)
        sources = {h.chunk.id: Source(id=h.chunk.id, title=h.chunk.title) for h in hits}
        top = hits[0].chunk
        if self.llm is None:  # retrieval-only baseline
            return Response(
                answer=f"{top.title}: {top.text}",
                intent=Intent.RULE,
                sources=[sources[top.id]],
                path="retrieval",
                confidence=None,
            )
        prompt = build_prompt(question, hits, self.prompt_version)
        for attempt in range(self.retries + 1):
            try:
                raw = self.llm.complete(prompt)
                if self.tool_runner is not None:
                    try:
                        result = self.tool_runner(raw)
                    except InvalidRequest as exc:
                        return Response(answer=str(exc), intent=Intent.FEE, path="tool", degraded=True)
                    if result is not None:
                        return Response(answer=result, intent=Intent.FEE, path="tool")
                draft: AnswerDraft = parse_draft(raw, set(sources))
                if draft.abstain:
                    return Response(
                        answer=ESCALATE_MSG,
                        intent=Intent.UNKNOWN,
                        path="abstain",
                        escalate=True,
                        confidence=draft.confidence,
                    )
                return Response(
                    answer=draft.answer,
                    intent=Intent.RULE,
                    path="llm",
                    confidence=draft.confidence,
                    sources=[sources[i] for i in draft.source_ids],
                )
            except ProviderError as exc:
                log.warning("llm attempt %d failed: %s", attempt + 1, exc)
        return Response(
            answer=f"{top.title}: {top.text}",
            intent=Intent.RULE,
            sources=[sources[top.id]],
            path="retrieval",
            degraded=True,
        )
