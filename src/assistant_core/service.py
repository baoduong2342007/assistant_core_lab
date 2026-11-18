"""Core orchestrator: AssistantService."""

import logging

from assistant_core.config import Settings
from assistant_core.errors import InvalidRequest, ProviderError
from assistant_core.guard import PRIVATE_REPLY, is_private_request
from assistant_core.knowledge import Handbook, OfficeDirectory
from assistant_core.llm import StubLLM
from assistant_core.models import Intent, Message, Response, Source
from assistant_core.rag.answerer import RagAnswerer
from assistant_core.rag.chunker import load_folder
from assistant_core.rag.index import make_index
from assistant_core.responder import Responder, StubLLMResponder, TemplateResponder
from assistant_core.router import route
from assistant_core.tools import parse_credits, tuition

log = logging.getLogger("assistant_core")


class AssistantService:
    """Central entry point coordinating routing, knowledge retrieval, and response generation."""

    def __init__(
        self,
        settings: Settings,
        offices: OfficeDirectory,
        handbook: Handbook,
        responder: Responder,
        rag: RagAnswerer | None = None,
    ):
        self.rag = rag
        self.settings = settings
        self.offices = offices
        self.handbook = handbook
        self.responder = responder
        self.fallback = TemplateResponder()

    def list_rules(self) -> Response:
        """List the loaded handbook titles in their original order."""
        rules = self.handbook.rules
        titles = [rule.title for rule in rules]
        return Response(
            answer="\n".join(f"- {title}" for title in titles) if titles else "No handbook rules available.",
            intent=Intent.RULE,
            sources=[Source(id=rule.id, title=rule.title) for rule in rules],
            degraded=False,
        )

    def handle(self, msg: Message) -> Response:
        """Process an incoming user message and return a structured Response."""
        if self.rag is not None and is_private_request(msg.text):
            return Response(answer=PRIVATE_REPLY, intent=Intent.UNKNOWN, path="abstain", escalate=False, confidence=0.0)
        intent = route(msg.text, self.offices.names, policy_search=self.rag is not None)

        if intent is Intent.GREETING:
            return Response(
                answer="Hello! I can help with offices, fees and rules.",
                intent=intent,
                sources=[],
                degraded=False,
            )

        if intent is Intent.FEE:
            return self._fee(msg.text)

        if intent is Intent.OFFICE:
            o = self.offices.find(msg.text)
            if o is not None:
                return Response(
                    answer=f"{o.name}: room {o.room}, open {o.hours}.",
                    intent=intent,
                    sources=[],
                    degraded=False,
                )
            return Response(
                answer="Sorry, I could not find that office.",
                intent=Intent.UNKNOWN,
                sources=[],
                degraded=False,
            )

        return self._rule(msg.text)

    def _fee(self, text: str) -> Response:
        try:
            credits_n, retake_n = parse_credits(text)
            total = tuition(
                credits=credits_n,
                retake=retake_n,
                rate=self.settings.credit_rate_vnd,
                retake_multiplier=self.settings.retake_multiplier,
                max_credits=self.settings.max_credits,
            )
            return Response(
                answer=f"Your tuition is {total:,} VND.",
                intent=Intent.FEE,
                sources=[],
                degraded=False,
            )
        except InvalidRequest as exc:
            return Response(
                answer=str(exc),
                intent=Intent.FEE,
                sources=[],
                degraded=False,
            )

    def _rule(self, text: str) -> Response:
        rule = self.handbook.get_by_id(text)
        if rule is None and self.rag is not None:
            return self.rag.answer(text)
        rule = rule or self.handbook.search(text)
        if rule is None:
            return Response(
                answer="Sorry, I don't know that yet.",
                intent=Intent.UNKNOWN,
                sources=[],
                degraded=False,
            )

        sources = [Source(id=rule.id, title=rule.title)]
        try:
            answer = self.responder.explain(text, rule)
            return Response(
                answer=answer,
                intent=Intent.RULE,
                sources=sources,
                degraded=False,
            )
        except ProviderError:
            log.warning("provider failed; using template fallback")
            answer = self.fallback.explain(text, rule)
            return Response(
                answer=answer,
                intent=Intent.RULE,
                sources=sources,
                degraded=True,
            )


def build_service(settings: Settings, fail_provider: bool = False) -> AssistantService:
    """Convenience factory creating a standard AssistantService instance from settings."""
    d = settings.data_dir
    offices = OfficeDirectory.from_csv(d / "offices.csv")
    handbook = Handbook.from_json(d / "handbook.json")
    if settings.llm_provider == "stub":
        responder = StubLLMResponder(fail=fail_provider)
    else:
        responder = TemplateResponder()
    kb_dir = settings.kb_dir or (settings.data_dir / "kb")
    rag = None
    if kb_dir.is_dir():
        index = make_index(settings.retrieval_kind, load_folder(kb_dir))
        llm = StubLLM(fail=fail_provider) if settings.llm_provider == "stub" else None
        rag = RagAnswerer(index, llm, settings.retrieval_min_score, prompt_version=settings.prompt_version)
    return AssistantService(settings, offices, handbook, responder, rag)
