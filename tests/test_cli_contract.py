"""Dương's subprocess acceptance cases for CL-03/CL-04 integration."""

import json
import os
import subprocess
import sys

import pytest


@pytest.fixture
def cli_env(project_root):
    """Isolate the CLI from personal environment and .env settings."""
    return {
        **os.environ,
        "PYTHONPATH": str(project_root / "src"),
        "ASSISTANT_DATA_DIR": str(project_root / "data"),
        "LLM_PROVIDER": "stub",
        "LLM_API_KEY": "cli-test-secret-do-not-log",
        "CREDIT_RATE_VND": "450000",
        "RETAKE_MULTIPLIER": "1.5",
        "MAX_CREDITS": "30",
        "LOG_LEVEL": "INFO",
    }


def run_cli(args, env, cwd, input_text=None):
    return subprocess.run(
        [sys.executable, "-m", "assistant_core", *args],
        env=env,
        cwd=cwd,
        input=input_text,
        capture_output=True,
        text=True,
        timeout=10,
    )


@pytest.mark.parametrize(
    ("args", "expected"),
    [
        (["   "], "Query cannot be empty"),
        (["x" * 2001], "Runtime error"),
        (["--credit-rate", "0", "tuition 18 credits"], "Startup error"),
        (["--credit-rate", "-1", "tuition 18 credits"], "Startup error"),
        (["--log-level", "not-a-level", "hi"], "Startup error"),
    ],
)
def test_cli_expected_errors_have_no_traceback(args, expected, cli_env, tmp_path):
    proc = run_cli(args, cli_env, tmp_path)
    assert proc.returncode == 1
    assert proc.stdout == ""
    assert expected in proc.stderr
    assert "Traceback" not in proc.stderr
    assert cli_env["LLM_API_KEY"] not in proc.stderr


@pytest.mark.parametrize("failure", ["missing_data", "invalid_config"])
def test_cli_startup_failure(cli_env, tmp_path, failure):
    if failure == "missing_data":
        cli_env["ASSISTANT_DATA_DIR"] = str(tmp_path / "missing")
    else:
        cli_env["CREDIT_RATE_VND"] = "not-an-integer"
    proc = run_cli(["hi"], cli_env, tmp_path)
    assert proc.returncode == 1
    assert proc.stdout == ""
    assert "Startup error:" in proc.stderr
    assert "Traceback" not in proc.stderr


def test_cli_argparse_exit_code(cli_env, tmp_path):
    proc = run_cli(["--not-a-real-option"], cli_env, tmp_path)
    assert proc.returncode == 2
    assert "usage:" in proc.stderr


@pytest.mark.parametrize("input_text", ["", "quit\n", "\nhi\nquit\n"])
def test_cli_interactive_eof_quit_and_blank_lines(cli_env, tmp_path, input_text):
    proc = run_cli([], cli_env, tmp_path, input_text)
    assert proc.returncode == 0
    assert "Assistant ready" in proc.stdout
    assert "Traceback" not in proc.stderr
    if "hi" in input_text:
        assert "Hello!" in proc.stdout


def test_cli_interactive_recovers_after_validation_error(cli_env, tmp_path):
    proc = run_cli([], cli_env, tmp_path, "x" * 2001 + "\nhi\nquit\n")
    assert proc.returncode == 0
    assert "Error:" in proc.stderr
    assert "Hello!" in proc.stdout


@pytest.mark.parametrize("fail_provider", [False, True])
def test_cli_rule_keeps_source_and_separates_log_streams(cli_env, tmp_path, fail_provider):
    query = "can I register my thesis with 118 credits"
    args = ["--json"] + (["--fail-provider"] if fail_provider else []) + [query]
    proc = run_cli(args, cli_env, tmp_path)
    assert proc.returncode == 0
    response = json.loads(proc.stdout)
    assert response["intent"] == "rule"
    assert response["sources"] == [{"id": "H26-5.3", "title": "Thesis registration"}]
    assert response["degraded"] is fail_provider
    records = [json.loads(line) for line in proc.stderr.splitlines()]
    handled = [record for record in records if record["msg"] == "handled"]
    assert len(handled) == 1
    assert handled[0]["intent"] == "rule"
    assert handled[0]["session"] == "local"
    assert handled[0]["degraded"] is fail_provider
    assert handled[0]["latency_ms"] >= 0
    assert query not in proc.stderr
    assert cli_env["LLM_API_KEY"] not in proc.stdout + proc.stderr


def test_cli_unknown_has_no_source_or_degraded_flag(cli_env, tmp_path):
    proc = run_cli(["--json", "zzzz qqqq"], cli_env, tmp_path)
    assert proc.returncode == 0
    response = json.loads(proc.stdout)
    assert response["intent"] == "unknown"
    assert response["sources"] == []
    assert response["degraded"] is False
