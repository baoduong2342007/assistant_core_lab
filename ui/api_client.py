"""A tiny HTTP client for the assistant API. The UI talks to the backend ONLY through this class."""

from __future__ import annotations

import os
from dataclasses import dataclass, field

import httpx


@dataclass
class ChatResult:
    """Normalized result returned by ``AssistantClient.ask``."""

    ok: bool
    answer: str = ""
    intent: str = ""
    sources: list[dict] = field(default_factory=list)
    path: str = ""
    escalate: bool = False
    degraded: bool = False
    request_id: str = ""
    error: str = ""


class AssistantClient:
    """HTTP boundary for the Streamlit UI."""

    def __init__(
        self,
        base_url: str | None = None,
        timeout_s: float = 20.0,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        raw_url = base_url if base_url is not None else os.getenv("ASSISTANT_API_URL", "http://127.0.0.1:8000")
        resolved_url = raw_url.strip().rstrip("/")
        if not resolved_url.startswith(("http://", "https://")):
            raise ValueError("ASSISTANT_API_URL must start with http:// or https://")
        self._http = httpx.Client(base_url=resolved_url, timeout=timeout_s, transport=transport)
        self.last_feedback_error: str = ""
        self.health_error: str = ""

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> AssistantClient:
        return self

    def __exit__(self, *_exc: object) -> None:
        self.close()

    def ask(self, message: str, session_id: str) -> ChatResult:
        try:
            r = self._http.post("/v1/chat", json={"message": message, "session_id": session_id})
        except httpx.TimeoutException:
            return ChatResult(ok=False, error="The assistant is taking too long. Please try again.")
        except httpx.HTTPError:
            return ChatResult(ok=False, error="Cannot reach the assistant. Is the backend running?")

        if r.status_code == 422:
            return ChatResult(ok=False, error="Please type a question (1–2000 characters).")
        if r.status_code == 429:
            return ChatResult(ok=False, error="Too many questions in a short time. Please wait a minute.")
        if r.status_code != 200:
            return ChatResult(ok=False, error=f"Something went wrong on our side (error {r.status_code}).")

        try:
            d = r.json()
            return ChatResult(
                ok=True,
                answer=d["answer"],
                intent=d["intent"],
                sources=d.get("sources", []),
                path=d.get("path") or "",
                escalate=bool(d.get("escalate", False)),
                degraded=bool(d.get("degraded", False)),
                request_id=d["request_id"],
            )
        except (ValueError, KeyError, TypeError):
            return ChatResult(ok=False, error="Received an unexpected response from the assistant.")

    def send_feedback(self, request_id: str, rating: int, comment: str | None = None) -> bool:
        try:
            r = self._http.post("/v1/feedback", json={"request_id": request_id, "rating": rating, "comment": comment})
        except httpx.TimeoutException:
            self.last_feedback_error = "Saving feedback timed out. Please try again."
            return False
        except httpx.HTTPError:
            self.last_feedback_error = "Cannot reach the assistant backend to save feedback. Please try again."
            return False

        if r.status_code == 201:
            self.last_feedback_error = ""
            return True
        if r.status_code == 404:
            self.last_feedback_error = (
                "Could not find this response on the server (error 404). Please try again or ask a new question."
            )
            return False
        self.last_feedback_error = f"Could not save your feedback (error {r.status_code}). Please try again."
        return False

    def healthy(self) -> bool:
        try:
            ok = self._http.get("/health").status_code == 200
        except httpx.HTTPError:
            ok = False
        if ok:
            self.health_error = ""
            return True
        self.health_error = (
            "The assistant backend is not reachable. "
            "Start it with: python -m uvicorn assistant_api.main:create_app --factory"
        )
        return False
