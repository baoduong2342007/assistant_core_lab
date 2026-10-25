"""Exact ID lookup uses production knowledge, service and CLI paths."""

import json
import os
import subprocess
import sys

import pytest

from assistant_core.knowledge import Handbook
from assistant_core.models import Intent, Message, Rule


@pytest.mark.parametrize("query", ["H26-5.3", "h26-5.3", "  H26-5.3 "])
def test_handbook_exact_id(sample_handbook, query):
    assert sample_handbook.get_by_id(query).id == "H26-5.3"


@pytest.mark.parametrize("query", ["", "   ", "H99-9.9", "H26-5", "thesis"])
def test_handbook_id_miss(sample_handbook, query):
    assert sample_handbook.get_by_id(query) is None


def test_empty_handbook():
    assert Handbook([]).get_by_id("H26-5.3") is None


def test_normalize_stored_id():
    rule = Rule(id=" H26-5.3 ", title="Thesis", text="Example")
    assert Handbook([rule]).get_by_id("h26-5.3") is rule


@pytest.mark.parametrize("failing", [False, True])
def test_service_id_lookup(service, stub_responder_success, stub_responder_fail, failing):
    service.responder = stub_responder_fail if failing else stub_responder_success
    response = service.handle(Message(text=" h26-5.3 "))
    rule = service.handbook.get_by_id("H26-5.3")
    assert response.intent is Intent.RULE
    assert response.degraded is failing
    assert [(s.id, s.title) for s in response.sources] == [(rule.id, rule.title)]
    expected = service.fallback if failing else stub_responder_success
    assert response.answer == expected.explain("question", rule)


def test_service_unknown_id(service):
    response = service.handle(Message(text="H99-9.9"))
    assert response.intent is Intent.UNKNOWN
    assert response.sources == []
    assert response.degraded is False


@pytest.mark.parametrize("failing", [False, True])
def test_cli_id_lookup(project_root, tmp_path, failing):
    env = {
        **os.environ,
        "PYTHONPATH": str(project_root / "src"),
        "ASSISTANT_DATA_DIR": str(project_root / "data"),
        "LLM_PROVIDER": "stub",
        "CREDIT_RATE_VND": "450000",
        "RETAKE_MULTIPLIER": "1.5",
        "MAX_CREDITS": "30",
        "LOG_LEVEL": "INFO",
    }
    args = [sys.executable, "-m", "assistant_core", "--json"]
    if failing:
        args.append("--fail-provider")
    proc = subprocess.run([*args, "h26-5.3"], env=env, cwd=tmp_path, capture_output=True, text=True, timeout=10)
    assert proc.returncode == 0, proc.stderr
    response = json.loads(proc.stdout)
    assert response["intent"] == "rule"
    assert response["sources"][0]["id"] == "H26-5.3"
    assert response["degraded"] is failing
