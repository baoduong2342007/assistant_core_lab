"""Configuration and environment variable management."""

import os
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from assistant_core.errors import ConfigError


class Settings(BaseModel):
    """Validated offline configuration; never serialize this model into logs."""

    model_config = ConfigDict(hide_input_in_errors=True)

    data_dir: Path = Path("data")
    llm_provider: Literal["stub", "template"] = "stub"
    llm_api_key: str | None = Field(default=None, repr=False, exclude=True)
    credit_rate_vnd: int = Field(default=450_000, gt=0)
    retake_multiplier: float = Field(default=1.5, gt=0, allow_inf_nan=False)
    max_credits: int = Field(default=30, gt=0)
    api_admin_key: str | None = Field(default=None, repr=False, exclude=True)
    weather_url: str = "https://api.open-meteo.com/v1/forecast"
    weather_timeout_s: float = Field(default=3.0, gt=0, allow_inf_nan=False)
    campus_lat: float = Field(default=10.7626, ge=-90, le=90)
    campus_lon: float = Field(default=106.6822, ge=-180, le=180)
    rate_limit_per_min: int = Field(default=30, gt=0)
    log_level: str = "INFO"

    @field_validator("credit_rate_vnd", "max_credits", mode="before")
    @classmethod
    def validate_integer(cls, value: object) -> object:
        """Reject decimal environment strings instead of silently coercing them."""
        if isinstance(value, str):
            return int(value)
        return value

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        valid = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
        level = v.strip().upper()
        if level not in valid:
            raise ValueError(f"log_level must be one of {', '.join(valid)}")
        return level


def load_settings(env_file: str | Path | None = ".env") -> Settings:
    """Load defaults < .env < existing environment; report expected errors safely."""
    try:
        if env_file:
            load_dotenv(env_file, override=False)
    except (OSError, UnicodeError) as exc:
        raise ConfigError("Cannot read the environment file") from exc

    try:
        return Settings(
            data_dir=os.getenv("ASSISTANT_DATA_DIR", "data"),
            llm_provider=os.getenv("LLM_PROVIDER", "stub"),
            llm_api_key=os.getenv("LLM_API_KEY") or None,
            credit_rate_vnd=os.getenv("CREDIT_RATE_VND", "450000"),
            retake_multiplier=os.getenv("RETAKE_MULTIPLIER", "1.5"),
            max_credits=os.getenv("MAX_CREDITS", "30"),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            api_admin_key=os.getenv("API_ADMIN_KEY") or None,
            weather_url=os.getenv("WEATHER_URL", "https://api.open-meteo.com/v1/forecast"),
            weather_timeout_s=os.getenv("WEATHER_TIMEOUT_S", "3"),
            campus_lat=os.getenv("CAMPUS_LAT", "10.7626"),
            campus_lon=os.getenv("CAMPUS_LON", "106.6822"),
            rate_limit_per_min=os.getenv("RATE_LIMIT_PER_MIN", "30"),
        )
    except ValidationError as exc:
        fields = ", ".join(str(error["loc"][0]) for error in exc.errors())
        # Do not stringify ValidationError: it can contain environment input values.
        raise ConfigError(f"Invalid configuration: {fields}") from exc
