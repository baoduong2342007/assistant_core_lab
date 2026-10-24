"""Integration tests for the command-line interface."""

import json
import subprocess
import sys


def test_cli_execution_tuition():
    cmd = [
        sys.executable,
        "-m",
        "assistant_core",
        "tuition for 18 credits and 2 retake",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
    assert "Your tuition is 9,450,000 VND." in proc.stdout
    # Logs are routed to stderr as JSON
    assert '"intent": "fee"' in proc.stderr


def test_cli_execution_greeting():
    cmd = [sys.executable, "-m", "assistant_core", "hi"]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
    assert "Hello! I can help with offices, fees and rules." in proc.stdout
    assert '"intent": "greeting"' in proc.stderr


def test_cli_execution_json_flag():
    cmd = [
        sys.executable,
        "-m",
        "assistant_core",
        "--json",
        "where is the library",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
    data = json.loads(proc.stdout)
    assert data["intent"] == "office"
    assert "B.201" in data["answer"]
    assert data["degraded"] is False


def test_cli_execution_fallback():
    cmd = [
        sys.executable,
        "-m",
        "assistant_core",
        "--fail-provider",
        "can I register my thesis with 118 credits",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
    assert "Thesis registration:" in proc.stdout
    assert '"degraded": true' in proc.stderr


def test_cli_invalid_arg():
    cmd = [sys.executable, "-m", "assistant_core", "--invalid-flag-123"]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    assert proc.returncode != 0
