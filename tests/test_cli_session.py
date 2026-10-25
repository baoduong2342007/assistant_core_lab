"""Huy's H1: validated per-run session context in both CLI modes."""

import json
import logging
import os
import subprocess
import sys

import pytest

from assistant_core.__main__ import main


@pytest.fixture
def session_env(project_root):
    """Explicit subprocess settings independent of the user's .env."""
    return {
        **os.environ,
        "PYTHONPATH": str(project_root / "src"),
        "ASSISTANT_DATA_DIR": str(project_root / "data"),
        "LLM_PROVIDER": "stub",
        "LLM_API_KEY": "fake-secret-for-session-tests",
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


@pytest.mark.parametrize("session", ["run-42", "A_1", "x" * 64, "  run-42  "])
def test_session_metadata_preserves_json_response(session, session_env, tmp_path):
    query = "zzzz private-student-question"
    result = run_cli(["--session-id", session, "--json", query], session_env, tmp_path)
    assert result.returncode == 0
    response = json.loads(result.stdout)
    assert set(response) == {"answer", "intent", "sources", "degraded"}
    assert response["intent"] == "unknown"
    record = json.loads(result.stderr)
    assert record["session"] == session.strip()
    assert record["intent"] == response["intent"]
    assert query not in result.stderr
    assert session_env["LLM_API_KEY"] not in result.stdout + result.stderr


@pytest.mark.parametrize("session", ["", "   ", "x" * 65, "private message", "x\ny", "-start", "Huy/1", "phiên"])
def test_invalid_session_is_usage_error_before_startup(session, session_env, tmp_path):
    session_env["ASSISTANT_DATA_DIR"] = str(tmp_path / "missing")
    result = run_cli([f"--session-id={session}", "hi"], session_env, tmp_path)
    assert result.returncode == 2
    assert result.stdout == ""
    assert "session ID must be" in result.stderr
    assert "Traceback" not in result.stderr
    assert "Startup error" not in result.stderr
    assert "private message" not in result.stderr


def test_interactive_requests_keep_same_session(session_env, tmp_path):
    result = run_cli(["--session-id", "interactive-1"], session_env, tmp_path, "hi\nwhere is the library\nquit\n")
    assert result.returncode == 0
    assert "Hello!" in result.stdout and "B.201" in result.stdout
    records = [json.loads(line) for line in result.stderr.splitlines()]
    assert [record["session"] for record in records] == ["interactive-1", "interactive-1"]
    assert [record["intent"] for record in records] == ["greeting", "office"]


def test_default_session_remains_local(session_env, tmp_path):
    result = run_cli(["hi"], session_env, tmp_path)
    assert result.returncode == 0
    assert json.loads(result.stderr)["session"] == "local"


def test_log_level_override_only_affects_this_run(session_env, tmp_path):
    session_env["LOG_LEVEL"] = "ERROR"
    visible = run_cli(["--session-id", "one", "--log-level", "info", "hi"], session_env, tmp_path)
    hidden = run_cli(["--session-id", "two", "hi"], session_env, tmp_path)
    assert visible.returncode == hidden.returncode == 0
    assert json.loads(visible.stderr)["session"] == "one"
    assert hidden.stderr == ""
    assert visible.stdout == hidden.stdout
    assert session_env["LOG_LEVEL"] == "ERROR"


def test_same_process_repeated_main_does_not_duplicate_logs(session_env, tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    for name, value in session_env.items():
        monkeypatch.setenv(name, value)
    logger = logging.getLogger("assistant_core")
    handlers, level, propagate = logger.handlers[:], logger.level, logger.propagate
    logger.handlers = []
    try:
        assert main(["--session-id", "one", "hi"]) == 0
        assert main(["--session-id", "two", "hi"]) == 0
        captured = capsys.readouterr()
        records = [json.loads(line) for line in captured.err.splitlines()]
        assert [record["session"] for record in records] == ["one", "two"]
        assert len(captured.out.splitlines()) == 2
    finally:
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
            handler.close()
        logger.handlers, logger.level, logger.propagate = handlers, level, propagate
