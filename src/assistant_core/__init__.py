"""Assistant Core package.

A modular, testable, and maintainable Python service for academic assistant workflows.
"""

from assistant_core.config import Settings, load_settings
from assistant_core.errors import (
    AssistantError,
    ConfigError,
    DataError,
    InvalidRequest,
    ProviderError,
)
from assistant_core.models import Intent, Message, Response, Rule, Source
from assistant_core.service import AssistantService

__version__ = "0.3.0"

__all__ = [
    "AssistantError",
    "AssistantService",
    "ConfigError",
    "DataError",
    "Intent",
    "InvalidRequest",
    "Message",
    "ProviderError",
    "Response",
    "Rule",
    "Settings",
    "Source",
    "load_settings",
]
