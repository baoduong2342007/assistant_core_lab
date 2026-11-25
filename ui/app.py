"""Streamlit chat UI.   Run:  streamlit run ui/app.py      (the API must be running on port 8000)

The UI never imports assistant_core: it only talks to the backend through the HTTP API.
"""

import os
import sys
import uuid
from pathlib import Path

import streamlit as st

repo_root = str(Path(__file__).resolve().parents[1])
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from ui.api_client import AssistantClient  # noqa: E402
from ui.logic import EXAMPLES, WELCOME, build_status_note, format_sources, validate_input  # noqa: E402


def _handle_feedback(client: AssistantClient, request_id: str, rating: int, toast_message: str) -> None:
    """Send response feedback and update UI state only when the API accepts it."""
    if client.send_feedback(request_id, rating):
        st.session_state.rated.add(request_id)
        st.session_state.feedback_toast = toast_message
        st.rerun()
    st.warning("Could not send feedback. Please try again.")


def run(client: AssistantClient) -> None:
    # ---- session state: remembered between reruns of this script ----------------
    if "session_id" not in st.session_state:
        st.session_state.session_id = uuid.uuid4().hex[:12]
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": WELCOME}]
    if "rated" not in st.session_state:
        st.session_state.rated = set()

    st.title("🎓 FIT Study Assistant")
    if not client.healthy():
        st.error(
            "The assistant backend is not reachable. Start it with: uvicorn assistant_api.main:create_app --factory"
        )

    with st.sidebar:
        st.subheader("Try an example")
        for ex in EXAMPLES:
            if st.button(ex, use_container_width=True):
                st.session_state.pending = ex
        st.caption("This is an AI assistant (English queries). Check important decisions with the Training Office.")
        if st.button("New chat", key="new_chat", use_container_width=True):
            st.session_state.session_id = uuid.uuid4().hex[:12]
            st.session_state.messages = [{"role": "assistant", "content": WELCOME}]
            st.session_state.rated = set()
            st.rerun()

    # ---- history -------------------------------------------------------------------
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])
            if m.get("sources"):
                st.caption(m["sources"])
            if m.get("note"):
                st.info(m["note"])
            rid = m.get("request_id")
            if rid:
                feedback_slot = st.empty()
                if rid not in st.session_state.rated:
                    with feedback_slot.container():
                        c1, c2 = st.columns(2)
                        if c1.button("👍 Helpful", key=f"up-{rid}", use_container_width=True):
                            _handle_feedback(client, rid, 1, "Thanks for your feedback!")
                        if c2.button("👎 Not helpful", key=f"down-{rid}", use_container_width=True):
                            _handle_feedback(client, rid, -1, "Thanks — we will look at this answer.")
                else:
                    feedback_slot.caption("✓ Feedback recorded")

    if toast_message := st.session_state.pop("feedback_toast", None):
        st.toast(toast_message)

    # ---- new question ----------------------------------------------------------------
    chat_input_value = st.chat_input("Ask in English about fees, offices or the handbook…")
    pending_question = st.session_state.pop("pending", None)
    raw_question = chat_input_value if chat_input_value is not None else pending_question
    if raw_question is not None:
        question = raw_question.strip()
        problem = validate_input(question)
        if problem:
            st.warning(problem)
        else:
            st.session_state.messages.append({"role": "user", "content": question})
            with st.spinner("Thinking…"):
                result = client.ask(question, st.session_state.session_id)
            if result.ok:
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": result.answer,
                        "sources": format_sources(result.sources),
                        "note": build_status_note(result, question),
                        "request_id": result.request_id,
                    }
                )
            else:
                st.session_state.messages.append({"role": "assistant", "content": f"⚠️ {result.error}"})
            st.rerun()


st.set_page_config(page_title="FIT Study Assistant", page_icon="🎓")
with AssistantClient(os.getenv("ASSISTANT_API_URL", "http://127.0.0.1:8000")) as client:
    run(client)
