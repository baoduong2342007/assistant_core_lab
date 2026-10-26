"""Unit tests for tuition calculation tools."""

import pytest

from assistant_core.errors import InvalidRequest
from assistant_core.tools import parse_credits, tuition


def test_parse_with_retake():
    assert parse_credits("tuition for 18 credits and 2 retake") == (18, 2)


def test_parse_without_retake():
    assert parse_credits("fee for 15 credits") == (15, 0)


def test_parse_no_credits():
    with pytest.raises(InvalidRequest, match="How many credits?"):
        parse_credits("what is my tuition?")


def test_parse_negative_credits():
    with pytest.raises(InvalidRequest, match="Credits cannot be negative"):
        parse_credits("tuition for -5 credits")


def test_tuition_value():
    assert tuition(18, 2, 450_000, 1.5, 30) == 9_450_000


def test_tuition_no_retake():
    assert tuition(20, 0, 450_000, 1.5, 30) == 9_000_000


@pytest.mark.parametrize("credits_val", [0, 31, -1])
def test_tuition_out_of_range(credits_val):
    with pytest.raises(InvalidRequest):
        tuition(credits_val, 0, 450_000, 1.5, 30)


def test_tuition_negative_retake():
    with pytest.raises(InvalidRequest):
        tuition(15, -1, 450_000, 1.5, 30)


@pytest.mark.parametrize(
    "query",
    [
        "tuition 18.5 credits",
        "tuition 18 credits and 1.5 retake",
        "tuition .5 credits",
        "tuition 18 credits and .5 retake",
        "tuition 1e2 credits",
        "tuition 18 credits and 1e1 retake",
        "tuition 18/2 credits",
        "tuition 18,5 credits",
        "tuition 1_8 credits",
    ],
)
def test_parse_rejects_non_integer_expressions_without_truncation(query):
    with pytest.raises(InvalidRequest, match="must be integers"):
        parse_credits(query)


@pytest.mark.parametrize(
    ("query", "expected"),
    [
        ("tuition 18 credits and 0 retake", (18, 0)),
        ("tuition 2 retake and 18 credits", (18, 2)),
        ("tuition 2 retake and 2 credits", (2, 2)),
        ("TUITION 18 CREDITS AND 2 RETAKE?", (18, 2)),
    ],
)
def test_parse_preserves_valid_integer_queries(query, expected):
    assert parse_credits(query) == expected


def test_retake_count_alone_does_not_become_main_credits():
    with pytest.raises(InvalidRequest, match="How many credits"):
        parse_credits("tuition 2 retake")


@pytest.mark.parametrize("query", ["tuition - 1 credits", "tuition 18 credits and -2 retake"])
def test_parse_rejects_negative_counts(query):
    with pytest.raises(InvalidRequest, match="cannot be negative"):
        parse_credits(query)


@pytest.mark.parametrize("credits", [1, 30])
def test_tuition_accepts_inclusive_credit_boundaries(credits):
    assert tuition(credits, 0, 450_000, 1.5, 30) == credits * 450_000


@pytest.mark.parametrize(("credits", "retake"), [(18.5, 0), (18, 1.5), (True, 0), (18, False)])
def test_tuition_rejects_non_integer_counts(credits, retake):
    with pytest.raises(InvalidRequest, match="must be integers"):
        tuition(credits, retake, 450_000, 1.5, 30)
