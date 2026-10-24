"""Typed domain models and request/response structures."""

from enum import Enum

from pydantic import BaseModel, Field, field_validator


class Intent(str, Enum):
    GREETING = "greeting"
    FEE = "fee"
    OFFICE = "office"
    RULE = "rule"
    UNKNOWN = "unknown"


class Message(BaseModel):
    text: str = Field(min_length=1, max_length=2000)
    session_id: str = "local"

    @field_validator("text")
    @classmethod
    def validate_not_whitespace_only(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("text cannot be empty or whitespace only")
        return v


class Source(BaseModel):
    id: str
    title: str


class Response(BaseModel):
    answer: str
    intent: Intent
    sources: list[Source] = Field(default_factory=list)
    degraded: bool = False


class Rule(BaseModel):
    id: str
    title: str
    text: str
