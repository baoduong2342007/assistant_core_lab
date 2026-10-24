"""Unit and contract tests for H1 extension: Exact Rule Lookup by ID."""

from assistant_core.errors import ProviderError
from assistant_core.models import Intent, Response, Rule, Source
from assistant_core.responder import Responder


def find_rule_by_id(rules: list[Rule], rule_id: str) -> Rule | None:
    """Lookup a rule by exact identifier with whitespace stripping and case-normalization.

    Three improvements from initial AI proposal:
    1. Case and whitespace normalization on search id and target id.
    2. Returns None consistently when not found instead of raising generic Exception.
    3. Graceful handling of empty or malformed queries without crashing.
    """
    if not rule_id or not rule_id.strip():
        return None
    normalized_query = rule_id.strip().lower()
    for rule in rules:
        if rule.id.strip().lower() == normalized_query:
            return rule
    return None


def execute_lookup_by_id(
    rules: list[Rule],
    rule_id: str,
    responder: Responder,
    fallback_responder: Responder,
) -> Response:
    """Execute rule explanation for an exact rule ID lookup with fallback support."""
    rule = find_rule_by_id(rules, rule_id)
    if rule is None:
        return Response(
            answer="No regulation found matching the requested identifier.",
            intent=Intent.UNKNOWN,
            sources=[],
            degraded=False,
        )

    sources = [Source(id=rule.id, title=rule.title)]
    try:
        answer = responder.explain(f"explain regulation {rule.id}", rule)
        return Response(answer=answer, intent=Intent.RULE, sources=sources, degraded=False)
    except ProviderError:
        fallback_answer = fallback_responder.explain(f"explain regulation {rule.id}", rule)
        return Response(answer=fallback_answer, intent=Intent.RULE, sources=sources, degraded=True)


def test_find_rule_by_id_exact_match(dummy_rule):
    """Verify exact ID returns matching rule."""
    rules = [dummy_rule]
    found = find_rule_by_id(rules, "H26-5.3")
    assert found is not None
    assert found.id == "H26-5.3"
    assert found.title == dummy_rule.title


def test_find_rule_by_id_case_insensitive(dummy_rule):
    """Verify lowercase ID query matches uppercase rule id."""
    rules = [dummy_rule]
    found = find_rule_by_id(rules, "h26-5.3")
    assert found is not None
    assert found.id == "H26-5.3"


def test_find_rule_by_id_whitespace_stripping(dummy_rule):
    """Verify query with leading/trailing whitespace matches rule."""
    rules = [dummy_rule]
    found = find_rule_by_id(rules, "   H26-5.3 \n")
    assert found is not None
    assert found.id == "H26-5.3"


def test_find_rule_by_id_not_found(dummy_rule):
    """Verify non-existent ID safely returns None."""
    rules = [dummy_rule]
    found = find_rule_by_id(rules, "H99-9.9")
    assert found is None


def test_find_rule_by_id_empty_rules_list():
    """Verify empty rule collection safely returns None without error."""
    assert find_rule_by_id([], "H26-5.3") is None
    assert find_rule_by_id([], "") is None


def test_execute_lookup_by_id_success(dummy_rule, stub_responder_success, template_responder):
    """Verify successful lookup returns RULE intent and correct source."""
    res = execute_lookup_by_id(
        rules=[dummy_rule],
        rule_id="H26-5.3",
        responder=stub_responder_success,
        fallback_responder=template_responder,
    )
    assert res.intent == Intent.RULE
    assert not res.degraded
    assert len(res.sources) == 1
    assert res.sources[0].id == "H26-5.3"
    assert "Based on" in res.answer


def test_execute_lookup_by_id_fallback_on_provider_error(dummy_rule, stub_responder_fail, template_responder):
    """Verify lookup with failing provider triggers fallback, sets degraded=True, and preserves source."""
    res = execute_lookup_by_id(
        rules=[dummy_rule],
        rule_id="H26-5.3",
        responder=stub_responder_fail,
        fallback_responder=template_responder,
    )
    assert res.intent == Intent.RULE
    assert res.degraded is True
    assert len(res.sources) == 1
    assert res.sources[0].id == "H26-5.3"
    assert res.answer == f"{dummy_rule.title}: {dummy_rule.text}"


def test_execute_lookup_by_id_unknown(dummy_rule, stub_responder_success, template_responder):
    """Verify unknown rule ID yields UNKNOWN intent and empty sources."""
    res = execute_lookup_by_id(
        rules=[dummy_rule],
        rule_id="H99-9.9",
        responder=stub_responder_success,
        fallback_responder=template_responder,
    )
    assert res.intent == Intent.UNKNOWN
    assert not res.degraded
    assert len(res.sources) == 0
