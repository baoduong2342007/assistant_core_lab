"""Unit tests for responder provider error fallback and graceful degradation."""

from assistant_core.errors import ProviderError
from assistant_core.models import Intent, Response, Rule, Source
from assistant_core.responder import Responder


def execute_explain_with_fallback(
    responder: Responder,
    fallback_responder: Responder,
    question: str,
    rule: Rule,
) -> Response:
    """Helper representing the core service fallback mechanism for rule explanation."""
    sources = [Source(id=rule.id, title=rule.title)]
    try:
        answer = responder.explain(question, rule)
        return Response(answer=answer, intent=Intent.RULE, sources=sources, degraded=False)
    except ProviderError:
        fallback_answer = fallback_responder.explain(question, rule)
        return Response(answer=fallback_answer, intent=Intent.RULE, sources=sources, degraded=True)


def test_provider_success_no_degraded(dummy_rule, stub_responder_success, template_responder):
    """Verify normal responder success yields degraded=False and correct sources."""
    res = execute_explain_with_fallback(
        responder=stub_responder_success,
        fallback_responder=template_responder,
        question="Can I take thesis?",
        rule=dummy_rule,
    )
    assert not res.degraded
    assert res.intent == Intent.RULE
    assert len(res.sources) == 1
    assert res.sources[0].id == dummy_rule.id
    assert res.answer == f"Based on '{dummy_rule.title}': {dummy_rule.text}"


def test_provider_failure_fallback_retains_sources_and_sets_degraded(
    dummy_rule, stub_responder_fail, template_responder
):
    """Verify provider failure falls back to template, sets degraded=True, and retains sources."""
    res = execute_explain_with_fallback(
        responder=stub_responder_fail,
        fallback_responder=template_responder,
        question="Can I take thesis?",
        rule=dummy_rule,
    )
    assert res.degraded is True
    assert res.intent == Intent.RULE
    assert len(res.sources) == 1
    assert res.sources[0].id == dummy_rule.id
    assert res.sources[0].title == dummy_rule.title
    assert res.answer == f"{dummy_rule.title}: {dummy_rule.text}"
