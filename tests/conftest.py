"""Shared pytest fixtures for assistant_core tests."""

from pathlib import Path

import pytest

from assistant_core.config import Settings
from assistant_core.knowledge import Handbook, OfficeDirectory
from assistant_core.models import Rule
from assistant_core.responder import StubLLMResponder, TemplateResponder
from assistant_core.service import AssistantService


@pytest.fixture
def project_root() -> Path:
    return Path(__file__).resolve().parent.parent


@pytest.fixture
def sample_settings(project_root: Path) -> Settings:
    return Settings(
        data_dir=project_root / "data",
        llm_provider="stub",
        llm_api_key=None,
        credit_rate_vnd=450_000,
        retake_multiplier=1.5,
        max_credits=30,
        log_level="INFO",
    )


@pytest.fixture
def sample_offices(sample_settings: Settings) -> OfficeDirectory:
    return OfficeDirectory.from_csv(sample_settings.data_dir / "offices.csv")


@pytest.fixture
def sample_handbook(sample_settings: Settings) -> Handbook:
    return Handbook.from_json(sample_settings.data_dir / "handbook.json")


@pytest.fixture
def service(sample_settings, sample_offices, sample_handbook) -> AssistantService:
    responder = StubLLMResponder(fail=False)
    return AssistantService(
        settings=sample_settings,
        offices=sample_offices,
        handbook=sample_handbook,
        responder=responder,
    )


@pytest.fixture
def dummy_rule() -> Rule:
    return Rule(
        id="RULE-01",
        title="Test Rule",
        text="This is a test rule description for unit tests.",
    )


@pytest.fixture
def template_responder() -> TemplateResponder:
    """Fixture providing a deterministic template responder."""
    return TemplateResponder()


@pytest.fixture
def stub_responder_success() -> StubLLMResponder:
    """Fixture providing an offline stub responder in success mode."""
    return StubLLMResponder(fail=False)


@pytest.fixture
def stub_responder_fail() -> StubLLMResponder:
    """Fixture providing an offline stub responder in failure mode."""
    return StubLLMResponder(fail=True)
