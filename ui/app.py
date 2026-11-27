"""Streamlit chat UI. Run: python -m streamlit run ui/app.py

The UI never imports assistant_core or assistant_api: it talks to the backend only through HTTP.
"""

from __future__ import annotations

import sys
import uuid
from pathlib import Path

import streamlit as st

repo_root = str(Path(__file__).resolve().parents[1])
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from ui.api_client import AssistantClient  # noqa: E402
from ui.logic import EXAMPLES, WELCOME, format_sources, source_items, status_note, validate_input  # noqa: E402


def render_sources(message: dict) -> None:
    """Render concise citations and a collapsible source-details panel when sources exist."""
    if message.get("sources"):
        st.caption(message["sources"])
    items = message.get("source_list") or []
    if items:
        with st.expander(f"📚 Source details ({len(items)})"):
            for item in items:
                st.markdown(f"- **{item['category']}** · `{item['id']}` — {item['title']}")


def _submit_feedback(
    client: AssistantClient,
    message: dict,
    request_id: str,
    rating: int,
    feedback_area,
) -> None:
    """Send 👍/👎 feedback, lock buttons on HTTP 201, or retain retry option on error."""
    with st.spinner("Saving feedback…"):
        ok = client.send_feedback(request_id, rating)
    if ok:
        st.session_state.rated.add(request_id)
        st.session_state.feedback_errors.pop(request_id, None)
        message["feedback"] = "Thanks for your feedback!" if rating == 1 else "Thanks — we will look at this answer."
        feedback_area.empty()
        st.rerun()
    st.session_state.feedback_errors[request_id] = (
        client.last_feedback_error or "Could not save your feedback. Please try again."
    )


def render_history(client: AssistantClient) -> None:
    """Render conversation history, sources, notes, and per-response feedback controls."""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            render_sources(message)
            if message.get("note"):
                st.info(message["note"])
            request_id = message.get("request_id")
            if not request_id:
                continue
            feedback_area = st.empty()
            if request_id in st.session_state.rated:
                feedback_area.success(message.get("feedback", "Thanks for your feedback!"))
                continue
            with feedback_area.container():
                st.caption("Was this answer helpful?")
                c1, c2 = st.columns(2)
                if c1.button("👍 Helpful", key=f"up-{request_id}", use_container_width=True):
                    _submit_feedback(client, message, request_id, 1, feedback_area)
                if c2.button("👎 Not helpful", key=f"down-{request_id}", use_container_width=True):
                    _submit_feedback(client, message, request_id, -1, feedback_area)
            if request_id in st.session_state.feedback_errors:
                st.error(st.session_state.feedback_errors[request_id])


def run(client: AssistantClient) -> None:
    """Main Streamlit render loop."""
    if "session_id" not in st.session_state:
        st.session_state.session_id = uuid.uuid4().hex[:12]
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": WELCOME}]
    if "rated" not in st.session_state:
        st.session_state.rated = set()
    if "feedback_errors" not in st.session_state:
        st.session_state.feedback_errors = {}

    st.title("🎓 FIT Study Assistant")
    if not client.healthy():
        st.error(client.health_error)

    with st.sidebar:
        st.subheader("Try an example")
        example_question = None
        for example in EXAMPLES:
            if st.button(example, use_container_width=True):
                example_question = example
        st.caption("This is an AI assistant. Read the sources and check important decisions with the Training Office.")

    render_history(client)

    typed = st.chat_input("Ask about fees, offices or the handbook…")
    question = typed if typed is not None else example_question
    if question is None:
        return

    cleaned = question.strip()
    problem = validate_input(cleaned)
    if problem:
        st.warning(problem)
        return

    st.session_state.messages.append({"role": "user", "content": cleaned})
    with st.chat_message("user"):
        st.markdown(cleaned)
    with st.chat_message("assistant"), st.spinner("Thinking… Checking official documents and tools…"):
        result = client.ask(cleaned, st.session_state.session_id)

    if result.ok:
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": result.answer,
                "sources": format_sources(result.sources),
                "source_list": source_items(result.sources),
                "note": status_note(result),
                "request_id": result.request_id,
            }
        )
    else:
        st.session_state.messages.append({"role": "assistant", "content": f"⚠️ {result.error}"})
    st.rerun()


st.set_page_config(page_title="FIT Study Assistant", page_icon="🎓")
try:
    _client = AssistantClient()
except ValueError:
    st.error("The assistant connection is not configured correctly. Please check ASSISTANT_API_URL.")
    st.stop()
with _client:
    run(_client)
