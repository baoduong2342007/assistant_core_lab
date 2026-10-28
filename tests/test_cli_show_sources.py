"""Tests for optional source display in the CLI."""

import subprocess
import sys


def run_cli(*args: str, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "assistant_core", *args],
        input=input_text,
        capture_output=True,
        text=True,
        check=False,
    )


def test_show_sources_and_fallback():
    for extra in ([], ["--fail-provider"]):
        result = run_cli("--show-sources", *extra, "H26-5.3")
        assert result.returncode == 0
        assert "Sources:\n- H26-5.3: " in result.stdout
        assert '"intent": "rule"' in result.stderr


def test_show_sources_does_not_invent_sources():
    result = run_cli("--show-sources", "hi")
    assert result.returncode == 0
    assert "Sources:" not in result.stdout


def test_json_combination_is_rejected():
    result = run_cli("--json", "--show-sources", "hi")
    assert result.returncode == 2
    assert not result.stdout
    assert "--json already includes sources" in result.stderr


def test_interactive_mode_displays_sources():
    result = run_cli("--show-sources", input_text="H26-5.3\nquit\n")
    assert result.returncode == 0
    assert "Sources:\n- H26-5.3: " in result.stdout
