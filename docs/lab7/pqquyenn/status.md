# Lab 07 Status — Phan Quỳnh Quyền (`pqquyenn`)

- **Ngày đối chiếu:** 27/11/2026 (`Asia/Ho_Chi_Minh`)
- **Nhánh cá nhân:** `feat/lab07-personal-pqquyenn`
- **Mốc `main` xuất phát:** `fe0d569415c2c29317e99cc1d73d4d21425fbdf2`
- **Học liệu Lab 07 chính thức:** `CSC10014-at-fit-hcmus/public_materials` tại `ea80fc97f747cadecde2262c9fd934eb2393c082` (`lab07/`)

## 1. Kết quả baseline tại mốc trước khi sửa

- Chạy `python -m pytest -q` trên `fe0d569` (Windows, Python 3.11.9): **510 passed, 2 failed** (`tests/test_lab6_huy_config.py::test_lab6_dotenv_precedence[False]` và `[True]` do so sánh `str(settings.kb_dir) == "custom/kb"` với dấu `\` trên Windows, đúng như `PLAN_TUAN7.md` đã ghi nhận).
- Chạy CLI `LLM_PROVIDER=stub`: `python -m assistant_core "I lost my student card"` trả đúng `Student Affairs (room I.102)`, `50,000 VND`, `3 working days`.
- Chạy starter chính thức `ea80fc9` trước khi điền TODO:
  - Warm-up `practice/test_hello_streamlit.py`: **1 passed, 3 failed** (`test_u2_greeting`, `test_u3_counter_survives_reruns`, `test_u4_validation`).
  - UI `tests/test_ui.py`: **5 passed, 2 failed** (`NotImplementedError: L1`, `NotImplementedError: L2`).

## 2. Phần đã hoàn thành (bài cá nhân & phạm vi của Quyền)

- **Warm-up U1–U4 (`practice/hello_streamlit.py`, `practice/test_hello_streamlit.py`):** Giữ tiêu đề U1, chào theo tên đã strip ở U2, đếm số lần bấm bằng `st.session_state.count` ở U3, kiểm tra `credits > 30` ở U4. Đạt **4/4** cả khi chạy trong `practice/` và từ root.
- **UI Logic & đối chiếu KB (`ui/logic.py` — phạm vi tích hợp chính của Quyền):**
  - Giữ độc lập hoàn toàn với Streamlit (`ast` test kiểm tra không import `streamlit`, `assistant_core`, `assistant_api`).
  - **L1 (`format_sources`):** Trả `""` khi rỗng; trả `"Sources: <id> — <title>; ..."` khi có một hoặc nhiều nguồn.
  - **L2 (`status_note`):** Ưu tiên `escalate` tới `Training Office, room I.101` trước `degraded`, kể cả khi cả hai cờ đều `True`.
  - Đối chiếu câu mẫu và nội dung KB thật qua API: thesis (`118 credits` → `H26#5.3`, 120 tín chỉ, GPA 2.0), mất thẻ (`I lost my student card` → `S26#3`, `I.102`, `50,000 VND`), học phí (`9,450,000 VND`, nguồn rỗng), thư viện (`B.201`), câu ngoài phạm vi (`path=abstain`, `escalate=true`, `I.101`) và degraded fallback (`degraded=true`, giữ nguồn `H26#5.3`).
- **HTTP Client (`ui/api_client.py`) & Streamlit App (`ui/app.py`):**
  - Tách ranh giới HTTP qua `AssistantClient` dùng `ASSISTANT_API_URL`, validate URL/timeout/JSON response, xử lý timeout, mất kết nối, `422`, `429`, `500`, `404`.
  - Luồng gửi dùng chung cho `st.chat_input` và sidebar examples, strip trước khi validate và gửi, giữ `session_id` qua rerun, thêm nút `New chat`.
  - Hoàn thiện **F1 (`👎 Not helpful`)** và sửa nhánh `👍 Helpful` dùng cùng helper kiểm tra HTTP `201` trước khi khóa đánh giá, bọc trong `st.empty()` để ẩn cả hai nút ngay sau `st.rerun()` và giữ nút cho phép thử lại khi lỗi.
- **Kiểm thử, đóng gói & tài liệu:**
  - Cập nhật `requirements.txt` (`streamlit==1.39.0`), `pyproject.toml` (`pythonpath = [".", "src"]`, optional `ui`), `.github/workflows/ci.yml` (thêm `ui/` vào rà conflict markers và thêm bước warm-up AppTest), `README.md` (hướng dẫn hai terminal PowerShell).
  - Sửa `tests/test_lab6_huy_config.py` dùng `Path("custom/kb")` để chạy xanh trên cả Windows và Ubuntu CI.
  - Giữ nguyên 7 test đề ở `tests/test_ui.py` và bổ sung 51 test ở `tests/test_lab7_quyen_ui.py` (logic, `MockTransport`, `AppTest`, KB + SQLite persistence qua restart).

## 3. Kiểm chứng sau chỉnh sửa cuối cùng

Xem chi tiết log tại [tests.txt](tests.txt) và kết quả trình duyệt tại [demo_results.md](demo_results.md):

| Kiểm tra | Kết quả |
|---|---|
| `python -m pytest -q` | **570 passed**, 1 warning (`Starlette/AnyIO`) |
| `python -m pytest -q tests/test_ui.py` | **7 passed** |
| `python -m pytest -q tests/test_lab7_quyen_ui.py` | **51 passed**, 1 warning |
| `Push-Location practice; python -m pytest -q test_hello_streamlit.py` | **4 passed** |
| `python -m pytest -q practice/test_mini_search.py practice/test_hello_api.py practice/test_school_repo.py` | **14 passed**, 1 warning |
| `python practice/make_school_db.py; python practice/check.py` | **15/15** |
| `python eval/compare_paths.py --cases eval/cases_20.jsonl` | Retrieval **20/20**, LLM stub **20/20**, abstain **5/5** |
| `python eval/compare_paths.py` | Retrieval **45/45**, LLM stub **45/45**, abstain **15/15** |
| `ruff check .` / `ruff format --check .` / `ruff check --select BLE .` | Đạt cả 3 (89 files formatted) |
| Chrome + FastAPI/Streamlit thật (`1280x800` & `375x812`) | Đạt D.4, hai tab độc lập, 375px không tràn ngang, tắt/bật lại API giữ lịch sử và xác nhận feedback cũ |

## 4. Phần còn lại cần người thực hiện xác nhận trước khi chốt nộp

- **H1 (`user_test_observations.md`):** Hiện để trạng thái `PENDING`; cần Quyền mời 1 bạn ngoài nhóm dùng thử 10 phút với nhiệm vụ đã ghi sẵn, ghi 3 quan sát thật, sửa 1 lỗi UI/hệ thống thực tế và đính kèm commit + ảnh trước/sau. Không lấy kiểm thử tự động làm quan sát của người ngoài nhóm.
- **H2 (`reading.md`):** Đã chuẩn bị sẵn bản nháp **đúng 2 câu** liên kết hai chương Google PAIR (`Feedback + Control` và `Errors + Graceful Failure`); Quyền cần tự đọc 15 phút và rà lại/xác nhận hai câu này trước khi nộp chính thức.
- **Review & nộp bài:** Reviewer đề xuất theo `PLAN_TUAN7.md` là Minh (`luongnhatinh`). Chưa tự nhận peer approval hay nộp link trên LMS.
