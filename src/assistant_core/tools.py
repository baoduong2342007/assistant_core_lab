"""Deterministic computational tools for tuition calculations."""

import re

from assistant_core.errors import InvalidRequest


def parse_credits(text: str) -> tuple[int, int]:
    """Extract (credits, retake_credits) from query text.

    Examples:
        'tuition for 18 credits and 2 retake' -> (18, 2)
        'tuition 15 credits' -> (15, 0)
    """
    if re.search(r"-\d+", text):
        raise InvalidRequest("Credits cannot be negative.")

    retake_match = re.search(r"(\d+)\s*retake", text, re.IGNORECASE)
    retake_n = int(retake_match.group(1)) if retake_match else 0

    numbers = [int(n) for n in re.findall(r"\b\d+\b", text)]
    if retake_match and retake_n in numbers:
        numbers.remove(retake_n)

    if not numbers:
        raise InvalidRequest("How many credits?")

    credits_n = numbers[0]
    return credits_n, retake_n


def tuition(credits: int, retake: int, rate: int, retake_multiplier: float, max_credits: int) -> int:
    """Calculate total tuition deterministically.

    Formula:
        credits * rate + retake * rate * retake_multiplier
    """
    if not (1 <= credits <= max_credits):
        raise InvalidRequest(f"Credits must be between 1 and {max_credits}.")
    if retake < 0:
        raise InvalidRequest("Retake credits cannot be negative.")

    total = credits * rate + retake * rate * retake_multiplier
    return int(total)
