"""HTTP boundary for Streamlit; no imports from the backend implementation."""

from __future__ import annotations

import math
import os
from dataclasses import dataclass, field
from urllib.parse import urlsplit

import httpx
from pydantic import BaseModel, Field, ValidationError

DEFAULT_API_URL = "http://127.0.0.1:8000"


@dataclass
class ChatResult:
    ok: bool
    answer: str = ""
    intent: str = ""
    sources: list[dict] = field(default_factory=list)
    path: str = ""
    escalate: bool = False
    degraded: bool = False
    confidence: float | None = None
    request_id: str = ""
    error: str = ""


class _Source(BaseModel):
    id: str = Field(min_length=1)
    title: str


class _ChatPayload(BaseModel):
    answer: str
    intent: str
    sources: list[_Source] = Field(default_factory=list)
    path: str | None = None
    escalate: bool = False
    degraded: bool = False
    confidence: float | None = Field(default=None, ge=0, le=1, allow_inf_nan=False)
    request_id: str = Field(min_length=1)


def api_url(value: str | None = None) -> str:
    """Read UI-process configuration without loading the backend's dotenv file."""
    value = os.getenv("ASSISTANT_API_URL", DEFAULT_API_URL) if value is None else value
    try:
        # urlsplit rejects malformed IPv6 brackets that httpx would percent-encode.
        parsed = urlsplit(value.strip())
        _ = parsed.port
        url = httpx.URL(value.strip())
    except (httpx.InvalidURL, ValueError) as exc:
        raise ValueError("ASSISTANT_API_URL must be an absolute HTTP(S) URL") from exc
    if url.scheme not in ("http", "https") or not url.host or url.userinfo or url.query or url.fragment:
        raise ValueError("ASSISTANT_API_URL must be an HTTP(S) URL without credentials, query or fragment")
    return str(url).rstrip("/")


class AssistantClient:
    def __init__(
        self,
        base_url: str | None = None,
        timeout_s: float = 20.0,
        transport: httpx.BaseTransport | None = None,
    ):
        if not math.isfinite(timeout_s) or timeout_s <= 0:
            raise ValueError("timeout_s must be positive and finite")
        self._timeout_s = timeout_s
        self._http = httpx.Client(base_url=api_url(base_url), timeout=timeout_s, transport=transport)
        self.last_feedback_error = ""
        self.health_error = ""

    def __enter__(self) -> AssistantClient:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def close(self) -> None:
        self._http.close()

    def ask(self, message: str, session_id: str) -> ChatResult:
        message = message.strip()
        if not message or len(message) > 2000:
            return ChatResult(ok=False, error="Please type a question (1–2000 characters).")
        try:
            response = self._http.post("/v1/chat", json={"message": message, "session_id": session_id})
        except httpx.TimeoutException:
            return ChatResult(ok=False, error="The assistant is taking too long. Please try again shortly.")
        except httpx.HTTPError:
            return ChatResult(ok=False, error="Cannot reach the assistant backend. Please try again shortly.")
        if response.status_code == 422:
            return ChatResult(ok=False, error="Please type a question (1–2000 characters).")
        if response.status_code == 429:
            return ChatResult(ok=False, error="Too many questions in a short time. Please wait a minute and try again.")
        if response.status_code != 200:
            return ChatResult(
                ok=False,
                error=f"The assistant could not reply (error {response.status_code}). Please try again shortly.",
            )
        try:
            payload = _ChatPayload.model_validate_json(response.content, strict=True)
        except ValidationError:
            return ChatResult(ok=False, error="The assistant returned an unreadable reply. Please try again.")
        return ChatResult(
            ok=True,
            answer=payload.answer,
            intent=payload.intent,
            sources=[source.model_dump() for source in payload.sources],
            path=payload.path or "",
            escalate=payload.escalate,
            degraded=payload.degraded,
            confidence=payload.confidence,
            request_id=payload.request_id,
        )

    def send_feedback(self, request_id: str, rating: int, comment: str | None = None) -> bool:
        """Keep the starter's bool contract; expose a recovery message on failure."""
        self.last_feedback_error = ""
        if not request_id or type(rating) is not int or rating not in (-1, 1) or (comment and len(comment) > 500):
            self.last_feedback_error = "Please select Helpful or Not helpful for an available answer."
            return False
        try:
            response = self._http.post(
                "/v1/feedback", json={"request_id": request_id, "rating": rating, "comment": comment}
            )
        except httpx.TimeoutException:
            self.last_feedback_error = "Feedback confirmation took too long. Please try again."
            return False
        except httpx.HTTPError:
            self.last_feedback_error = "Cannot reach the assistant to save feedback. Please try again shortly."
            return False
        if response.status_code == 201:
            return True
        if response.status_code == 404:
            self.last_feedback_error = "This answer is no longer available for feedback. Please ask the question again."
        elif response.status_code == 429:
            self.last_feedback_error = "Too much feedback at once. Please wait a minute and try again."
        elif response.status_code == 422:
            self.last_feedback_error = "Feedback could not be accepted. Please ask the question again and retry."
        else:
            self.last_feedback_error = (
                f"Feedback could not be confirmed (error {response.status_code}). Please try again."
            )
        return False

    def healthy(self) -> bool:
        self.health_error = ""
        try:
            response = self._http.get("/health", timeout=min(2.0, self._timeout_s))
        except httpx.HTTPError:
            self.health_error = "The assistant is offline. Your conversation is kept here; please try again shortly."
            return False
        if response.status_code != 200:
            self.health_error = "The assistant is temporarily unavailable. Please try again shortly."
            return False
        return True
