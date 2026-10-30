"""Tests for listing handbook rules without search or provider calls."""

import json
import subprocess
import sys

from assistant_core.knowledge import Handbook
from assistant_core.models import Rule


def test_list_rules_uses_loaded_order_without_search_or_provider(service, monkeypatch):
    service.handbook = Handbook([Rule(id="2", title="Second", text="a"), Rule(id="1", title="First", text="b")])

    def fail(*args, **kwargs):
        raise AssertionError("provider or search must not be called")

    monkeypatch.setattr(service.responder, "explain", fail)
    monkeypatch.setattr(service.handbook, "search", fail)
    response = service.list_rules()
    assert response.answer == "- Second\n- First"
    assert [source.id for source in response.sources] == ["2", "1"]
    assert response.degraded is False


def test_list_rules_empty(service):
    service.handbook = Handbook([])
    response = service.list_rules()
    assert response.answer == "No handbook rules available."
    assert response.sources == []


def test_cli_list_rules_json():
    result = subprocess.run(
        [sys.executable, "-m", "assistant_core", "--list-rules", "--json"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert len(payload["sources"]) == 5
    assert payload["answer"].splitlines() == ["- " + source["title"] for source in payload["sources"]]


def test_cli_rejects_list_with_query():
    result = subprocess.run(
        [sys.executable, "-m", "assistant_core", "--list-rules", "hi"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 2
    assert not result.stdout
    assert "cannot be combined" in result.stderr
