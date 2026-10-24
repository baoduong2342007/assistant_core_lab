"""Configuration and environment variable management."""

import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, Field, field_validator

from assistant_core.errors import ConfigError


class Settings(BaseModel):
    data_dir: Path = Path("data")
    llm_provider: str = "stub"
    llm_api_key: str | None = Field(default=None, repr=False)  # never printed
    credit_rate_vnd: int = 450_000
    retake_multiplier: float = 1.5
    max_credits: int = 30
    log_level: str = "INFO"

    @field_validator("credit_rate_vnd")
    @classmethod
    def validate_rate(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("credit_rate_vnd must be positive")
        return v

    @field_validator("retake_multiplier")
    @classmethod
    def validate_multiplier(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("retake_multiplier must be positive")
        return v

    @field_validator("max_credits")
    @classmethod
    def validate_max_credits(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("max_credits must be positive")
        return v

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        valid = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if v.upper() not in valid:
            raise ValueError(f"log_level must be one of {valid}")
        return v.upper()


def load_settings(env_file: str | None = ".env") -> Settings:
    """Load settings from environment variables and optional .env file."""
    if env_file:
        load_dotenv(env_file, override=False)

    try:
        data_dir_env = os.getenv("ASSISTANT_DATA_DIR", "data")
        llm_provider_env = os.getenv("LLM_PROVIDER", "stub")
        llm_api_key_env = os.getenv("LLM_API_KEY") or None

        credit_rate_str = os.getenv("CREDIT_RATE_VND", "450000")
        try:
            credit_rate_val = int(credit_rate_str)
        except ValueError as exc:
            raise ConfigError(f"CREDIT_RATE_VND must be an integer, got {credit_rate_str!r}") from exc

        retake_mult_str = os.getenv("RETAKE_MULTIPLIER", "1.5")
        try:
            retake_mult_val = float(retake_mult_str)
        except ValueError as exc:
            raise ConfigError(f"RETAKE_MULTIPLIER must be a float, got {retake_mult_str!r}") from exc

        max_credits_str = os.getenv("MAX_CREDITS", "30")
        try:
            max_credits_val = int(max_credits_str)
        except ValueError as exc:
            raise ConfigError(f"MAX_CREDITS must be an integer, got {max_credits_str!r}") from exc

        log_level_env = os.getenv("LOG_LEVEL", "INFO")

        settings = Settings(
            data_dir=Path(data_dir_env),
            llm_provider=llm_provider_env,
            llm_api_key=llm_api_key_env,
            credit_rate_vnd=credit_rate_val,
            retake_multiplier=retake_mult_val,
            max_credits=max_credits_val,
            log_level=log_level_env,
        )
    except Exception as exc:
        if isinstance(exc, ConfigError):
            raise
        raise ConfigError(f"Configuration error: {exc}") from exc

    if settings.llm_provider != "stub" and not settings.llm_api_key:
        raise ConfigError(f"LLM_API_KEY is required when LLM_PROVIDER={settings.llm_provider!r}")

    return settings
