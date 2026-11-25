# Lab 07 Status — Lương Nhật Minh (`luongnhatinh`)

- **Date:** 2026-11-21
- **Branch:** `feat/lab07-personal-luongnhatinh`
- **Base `main` SHA:** `fe0d569`
- **Source `public_materials` Lab 07 SHA:** `ea80fc9`

## Completed Items

- **Warm-up (`practice/hello_streamlit.py`, `practice/test_hello_streamlit.py`):** Implemented U1–U4 (`"Hello, Streamlit 👋"` greeting, whitespace-stripped `name` greeting, `"Click me"` counter in `st.session_state.count`, and `credits > 30` advisor approval error vs. normal load info).
- **UI Logic & HTTP Client (`ui/logic.py`, `ui/api_client.py`):**
  - **L1 (`format_sources`):** Returns `""` for empty source lists or `"Sources: " + "; ".join(f"{s['id']} — {s['title']}" for s in sources)`.
  - **L2 (`status_note`):** Prioritizes `result.escalate` (`Training Office, room I.101`) over `result.degraded` (source-document fallback notice), returning `None` otherwise.
  - **`AssistantClient`:** Covers `GET /health`, `POST /v1/chat`, and `POST /v1/feedback` (`201`/`404`, `422`, `429`, `500`, timeouts, `httpx.HTTPError`, malformed JSON), normalizes `base_url`, and provides `close()` / context-manager cleanup.
- **Streamlit Chat App (`ui/app.py`):**
  - Preserves `session_id` per session, sidebar AI assistant disclaimer, and `use_container_width=True` example buttons.
  - Normalizes submitted input (`strip()`) before `validate_input` and `client.ask`, keeping whitespace-only input handled via `"Please type a question."` without calling the backend.
  - Implemented **F1 (`👎`)** and fixed the starter **`👍` bug** using a shared `_handle_feedback` helper: checks `client.send_feedback(rid, rating)` return value, marks `rid` rated and hides buttons immediately across `st.rerun()` with `st.toast` only on `True`, and shows a retry warning while keeping buttons visible on `False`.
- **Tests (`tests/test_ui.py`, `tests/test_ui_app.py`):**
  - `tests/test_ui.py` (13 tests): Retains all 7 starter tests and adds `AssistantClient` (`httpx.MockTransport` for 200/201/404/422/429/500/`TimeoutException`/`ConnectError`) and `ui.logic` coverage.
  - `tests/test_ui_app.py` (9 tests): Streamlit `AppTest` UI behavior checks plus real FastAPI + SQLite file-backed `create_app` persistence round-trips across restart.
- **Packaging, CI & Docs (`pyproject.toml`, `requirements.txt`, `.github/workflows/ci.yml`, `README.md`):**
  - Added `streamlit==1.39.0` to `requirements.txt`; updated `pyproject.toml` `pythonpath = [".", "src"]`.
  - Updated `.github/workflows/ci.yml` conflict-marker scan to include `ui/` and added `(cd practice && python -m pytest -q test_hello_streamlit.py)`.
  - Documented Lab 07 two-terminal local startup and check commands in `README.md`.
- **Personal Docs (`docs/lab7/luongnhatinh/`):**
  - `reading.md`: Drafted 2-sentence **H2** note grounded in Google PAIR Guidebook v2 (`Feedback + Control` and `Errors + Graceful Failure`).
  - `usability_checklist.md`: Verified and ticked all 10 pre-test usability items.

## Verification & Browser Check Summary (D.4 Matrix)

- **Automated Suites (`.venv\Scripts\python.exe` on Windows):**
  - `python -m pytest -q tests/test_ui.py tests/test_ui_app.py` → `22 passed`
  - `Push-Location practice; ..\.venv\Scripts\python.exe -m pytest -q test_hello_streamlit.py; Pop-Location` → `4 passed`
  - `python -m pytest -q practice/test_mini_search.py practice/test_hello_api.py practice/test_school_repo.py` → `14 passed`
  - `python -m pytest -q` → `532 passed, 2 failed` (only the 2 pre-existing Windows path-separator assertions in `tests/test_lab6_huy_config.py::test_lab6_dotenv_precedence[False|True]`, `'custom\\kb' == 'custom/kb'`)
  - `eval/compare_paths.py` (`LLM_PROVIDER=stub`) → `20/20` (`cases_20.jsonl`) and `45/45` (`cases.jsonl`)
  - `ruff check .`, `ruff format --check .`, `ruff check --select BLE .` → passed
- **Live Two-Server & Browser Verification:**
  - Verified live Uvicorn (`127.0.0.1:18000`, `LLM_PROVIDER=stub`) + Streamlit (`127.0.0.1:18501`) round-trips: `/health` (`200`), thesis registration (`H26#5.3`, 120 credits / 2.0 GPA), capital of France abstain (`Training Office, room I.101`), lost student card (`S26#3`, `I.102`), tuition calculation (`9,450,000 VND`), `POST /v1/feedback` (`201` for `1`/`-1`, `404` for unknown `request_id`), SQLite persistence across Uvicorn restart (`GET /v1/feedback`), and friendly offline error once backend stopped.
  - Inspected Streamlit UI in browser at desktop (`1280x800`) and phone (`375x812`) viewports. Minor non-blocking layout observations noted: `👍`/`👎` buttons stack vertically at `375px` width, and long chat history peeks ~15px under the fixed bottom chat input bar.

## H1 Usability Review & UI Fix (`2026-11-25`)

- **Synced teammate commit `f04b66a`:** Closed `AssistantClient` cleanly across Streamlit reruns via context manager, updated feedback buttons to `👍 Helpful` / `👎 Not helpful` with `request_id`-scoped keys, and fixed `tests/test_lab6_huy_config.py` Windows `Path` comparison.
- **Outside Reviewer 10-minute test:** Conducted at `850x694` viewport and documented in [usability_review_report.md](usability_review_report.md) with 6 `before` captures in `screenshots/before/` and instructions in [INSTRUCTION.md](INSTRUCTION.md).
- **UI Fix Commit (`fd7083b`):**
  - `ui/logic.py` & `ui/app.py`: Clarified English-only support in `WELCOME`, sidebar caption, and `st.chat_input` placeholder; fixed `"2 retakes"` in `EXAMPLES[1]`; added `looks_non_english()` and `build_status_note()` so escalated queries avoid duplicate `Training Office` banners and Vietnamese queries display an English-only rephrasing note; replaced `feedback_slot.empty()` with `feedback_slot.caption("✓ Feedback recorded")`; added sidebar `"New chat"` reset button (`key="new_chat"`).
  - `tests/test_ui.py` & `tests/test_ui_app.py`: Added coverage for `looks_non_english`, `build_status_note`, `"✓ Feedback recorded"`, Vietnamese escalation hint, and `"New chat"` reset.
- **Updated Verification (`.venv\Scripts\python.exe` on Windows, after `fd7083b`):**
  - `python -m pytest -q tests/test_ui.py tests/test_ui_app.py` → `24 passed, 1 warning`
  - `Push-Location practice; ..\.venv\Scripts\python.exe -m pytest -q test_hello_streamlit.py; Pop-Location` → `4 passed`
  - `python -m pytest -q` → `536 passed, 1 warning`
  - `ruff check .`, `ruff format --check .` (`89 files already formatted`), `ruff check --select BLE .` → passed
  - Browser `after` verification at `850x694`: [03_vietnamese_lost_card_after.png](screenshots/after/03_vietnamese_lost_card_after.png) and [06_feedback_recorded_and_new_chat_after.png](screenshots/after/06_feedback_recorded_and_new_chat_after.png).
- **Worksheet:** Completed [user_test_observations.md](user_test_observations.md) linking `fd7083b` and before/after screenshot pairs.

## Pending Personal Confirmation

- **Personal Review:** Minh's independent review of [reading.md](reading.md) (H2), PR diff, and LMS submission.
