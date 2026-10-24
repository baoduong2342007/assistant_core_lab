"""Unit tests for domain exceptions."""

from assistant_core.errors import (
    AssistantError,
    ConfigError,
    DataError,
    InvalidRequest,
    ProviderError,
)


def test_error_hierarchy():
    assert issubclass(ConfigError, AssistantError)
    assert issubclass(DataError, AssistantError)
    assert issubclass(InvalidRequest, AssistantError)
    assert issubclass(ProviderError, AssistantError)


def test_error_instantiation():
    err = ConfigError("bad config")
    assert str(err) == "bad config"
    assert isinstance(err, AssistantError)
