"""Streamlit chat UI. Run: python -m streamlit run ui/app.py (with FastAPI running).

The UI never imports assistant_core or assistant_api: all backend calls go through AssistantClient.
"""

import sys
import uuid
from pathlib import Path

import streamlit as st

repo_root = str(Path(__file__).resolve().parents[1])
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from ui.api_client import AssistantClient  # noqa: E402
from ui.logic import EXAMPLES, WELCOME, format_sources, status_note, validate_input  # noqa: E402


def _reset_session() -> None:
    st.session_state.session_id = uuid.uuid4().hex
    st.session_state.messages = [{"role": "assistant", "content": WELCOME}]
    st.session_state.rated = set()
    st.session_state.feedback_errors = {}


def _render_history(client: AssistantClient) -> None:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("sources"):
                st.caption(message["sources"])
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
                col_up, col_down = st.columns(2)
                rating = None
                if col_up.button("👍 Helpful", key=f"up-{request_id}", use_container_width=True):
                    rating = 1
                if col_down.button("👎 Not helpful", key=f"down-{request_id}", use_container_width=True):
                    rating = -1
            if rating is not None:
                with st.spinner("Saving feedback…"):
                    saved = client.send_feedback(request_id, rating)
                if saved:
                    st.session_state.rated.add(request_id)
                    message["feedback"] = (
                        "Thanks for your feedback!" if rating == 1 else "Thanks — we will look at this answer."
                    )
                    st.session_state.feedback_errors.pop(request_id, None)
                    feedback_area.empty()
                    st.toast(message["feedback"])
                    st.rerun()
                st.session_state.feedback_errors[request_id] = (
                    client.last_feedback_error or "Could not save feedback. Please try again."
                )
            if request_id in st.session_state.feedback_errors:
                st.error(st.session_state.feedback_errors[request_id])


def run(client: AssistantClient) -> None:
    """Render the Streamlit page and process one interaction per rerun."""
    if "session_id" not in st.session_state:
        _reset_session()
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
        selected_example = None
        for example in EXAMPLES:
            if st.button(example, use_container_width=True):
                selected_example = example
        st.caption("This is an AI assistant. Read the sources and check important decisions with the Training Office.")
        if st.button("New chat", key="new_chat", use_container_width=True):
            _reset_session()
            st.rerun()

    _render_history(client)

    typed = st.chat_input("Ask about fees, offices or the handbook…")
    raw_question = typed if typed is not None else selected_example
    if raw_question is None:
        return

    question = raw_question.strip()
    problem = validate_input(question)
    if problem:
        st.warning(problem)
        return

    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)
    with st.chat_message("assistant"), st.spinner("Thinking…"):
        result = client.ask(question, st.session_state.session_id)

    if result.ok:
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": result.answer,
                "sources": format_sources(result.sources),
                "note": status_note(result),
                "request_id": result.request_id,
            }
        )
    else:
        st.session_state.messages.append({"role": "assistant", "content": f"⚠️ {result.error}"})
    st.rerun()


st.set_page_config(page_title="FIT Study Assistant", page_icon="🎓")
try:
    client = AssistantClient()
except ValueError:
    st.error("Invalid ASSISTANT_API_URL configuration. Please check the URL and restart the UI.")
    st.stop()
with client:
    run(client)
