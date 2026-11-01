"""HTTP request/response schemas — the public API contract (v1)."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from assistant_core.models import Intent, Source


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000, examples=["tuition for 18 credits and 2 retake"])
    session_id: str = Field(default="anonymous", max_length=64)

    @field_validator("message")
    @classmethod
    def reject_whitespace(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("message cannot be whitespace only")
        return value


class ChatResponse(BaseModel):
    answer: str
    intent: Intent
    sources: list[Source] = Field(default_factory=list)
    degraded: bool = False
    request_id: str


class FeedbackIn(BaseModel):
    request_id: str = Field(min_length=1, max_length=64)
    rating: int = Field(ge=-1, le=1, description="-1 = thumbs down, 0 = neutral, 1 = thumbs up")
    comment: str | None = Field(default=None, max_length=500)


class FeedbackOut(FeedbackIn):
    id: int
    created_at: datetime


class Weather(BaseModel):
    temperature_c: float = Field(allow_inf_nan=False)
    wind_kmh: float = Field(ge=0, allow_inf_nan=False)
    description: str
    observed_at: str
    stale: bool = False  # True when served from cache after an upstream failure


class ErrorBody(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    error: ErrorBody
