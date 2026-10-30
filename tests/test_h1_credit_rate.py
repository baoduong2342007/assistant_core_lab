"""Tests for H1: CLI tuition credit rate override (--credit-rate)."""

import json
import subprocess
import sys


def test_cli_credit_rate_override_calculation():
    """Verify that --credit-rate overrides the default rate for calculations."""
    # 18 * 500_000 + 2 * 500_000 * 1.5 = 9_000_000 + 1_500_000 = 10_500_000 VND
    cmd = [
        sys.executable,
        "-m",
        "assistant_core",
        "--credit-rate",
        "500000",
        "tuition for 18 credits and 2 retake",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
    assert "10,500,000 VND" in proc.stdout


def test_cli_credit_rate_default_preserved():
    """Verify default rate (450,000 VND) is preserved when flag is omitted."""
    # 18 * 450_000 + 2 * 450_000 * 1.5 = 8_100_000 + 1_350_000 = 9_450_000 VND
    cmd = [
        sys.executable,
        "-m",
        "assistant_core",
        "tuition for 18 credits and 2 retake",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
    assert "9,450,000 VND" in proc.stdout


def test_cli_credit_rate_with_json_export():
    """Verify --credit-rate works in combination with --json."""
    cmd = [
        sys.executable,
        "-m",
        "assistant_core",
        "--credit-rate",
        "600000",
        "--json",
        "tuition 10 credits",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
    payload = json.loads(proc.stdout)
    assert payload["intent"] == "fee"
    assert "6,000,000 VND" in payload["answer"]


def test_cli_credit_rate_rejects_non_positive():
    """Verify --credit-rate rejects zero and negative values."""
    for bad_rate in ["0", "-50000"]:
        cmd = [
            sys.executable,
            "-m",
            "assistant_core",
            "--credit-rate",
            bad_rate,
            "tuition 10 credits",
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
        assert proc.returncode != 0
        assert "Startup error" in proc.stderr or "positive" in proc.stderr


def test_cli_credit_rate_rejects_invalid_type():
    """Verify non-integer rates are rejected by argument parser with exit 2."""
    cmd = [
        sys.executable,
        "-m",
        "assistant_core",
        "--credit-rate",
        "abc",
        "tuition 10 credits",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    assert proc.returncode == 2
    assert "invalid int value" in proc.stderr


def test_cli_credit_rate_interactive_mode():
    """Verify --credit-rate applies during interactive REPL session."""
    cmd = [
        sys.executable,
        "-m",
        "assistant_core",
        "--credit-rate",
        "500000",
    ]
    proc = subprocess.run(
        cmd,
        input="tuition 10 credits\nquit\n",
        capture_output=True,
        text=True,
        check=True,
    )
    assert "5,000,000 VND" in proc.stdout
