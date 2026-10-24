"""Unit tests for the intent router."""

import pytest

from assistant_core.models import Intent
from assistant_core.router import route

OFFICE_NAMES = {"training office", "student affairs", "library", "it helpdesk"}


@pytest.mark.parametrize("greeting", ["hi", "hello", "hey", "xin chao", "HELLO!"])
def test_route_greeting(greeting):
    assert route(greeting, OFFICE_NAMES) is Intent.GREETING


@pytest.mark.parametrize(
    "query",
    [
        "tuition for 18 credits",
        "how much is fee per credit?",
        "what is tuition?",
    ],
)
def test_route_fee(query):
    assert route(query, OFFICE_NAMES) is Intent.FEE


@pytest.mark.parametrize(
    "query",
    [
        "where is the library?",
        "student affairs opening hours",
        "contact IT helpdesk",
    ],
)
def test_route_office(query):
    assert route(query, OFFICE_NAMES) is Intent.OFFICE


@pytest.mark.parametrize(
    "query",
    [
        "can I register my thesis with 118 credits",
        "regulations on course retake",
        "what happens if I am absent from exam?",
    ],
)
def test_route_rule(query):
    assert route(query, OFFICE_NAMES) is Intent.RULE


def test_route_precedence():
    # Greetings take precedence even with punctuation
    assert route("hello, where is library?", OFFICE_NAMES) is Intent.OFFICE
    assert route("hello!", OFFICE_NAMES) is Intent.GREETING
