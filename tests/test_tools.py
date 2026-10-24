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
