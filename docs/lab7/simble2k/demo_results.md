# Lab 07 — Kết quả kiểm thử & Demo D.4 (`simble2k`)

- **Thành viên:** Phạm Quốc Bảo (`simble2k`)
- **Nhánh cá nhân:** `feat/lab07-personal-simble2k`
- **Mốc nền (`main`):** `fe0d569415c2c29317e99cc1d73d4d21425fbdf2`
- **Môi trường kiểm thử:** Windows, CPython `3.12.13` (`.venv` tạo bằng `uv`), `streamlit==1.39.0`, `LLM_PROVIDER=stub`

## 1. Kiểm thử tự động

| Lệnh | Kết quả quan sát |
|---|---|
| `Push-Location practice; ..\.venv\Scripts\python.exe -m pytest -q test_hello_streamlit.py; Pop-Location` | `4 passed in 0.62s` (`U1–U4`) |
| `.\.venv\Scripts\python.exe -m pytest -v tests/test_ui.py tests/test_lab7_bao_feedback.py` | `19 passed in 1.60s` (`7` test starter + `12` test F1/lỗi/SQLite persistence/Bonus) |
| `.\.venv\Scripts\python.exe -m pytest -q` | `529 passed, 2 failed` (2 lỗi duy nhất là lỗi có sẵn trên Windows ở `tests/test_lab6_huy_config.py::test_lab6_dotenv_precedence[False/True]`: `'custom\\kb' == 'custom/kb'`) |
| `.\.venv\Scripts\python.exe -m ruff check .` | `All checks passed!` |
| `.\.venv\Scripts\python.exe -m ruff format --check .` | `89 files already formatted` |
| `.\.venv\Scripts\python.exe -m ruff check --select BLE .` | `All checks passed!` |
| `$env:LLM_PROVIDER='stub'; .\.venv\Scripts\python.exe eval/compare_paths.py --cases eval/cases_20.jsonl` | `retrieval 20/20 (5/5 abstain)`, `llm (stub) 20/20 (5/5 abstain)` |
| `$env:LLM_PROVIDER='stub'; .\.venv\Scripts\python.exe -m assistant_core "I lost my student card"` | Trả lời `Student Affairs (room I.102)`, phí `50,000 VND`, `3 working days` |

## 2. Kết quả chạy thực tế 2 server & Ma trận D.4

Khởi chạy hai tiến trình thật ở local:
- Backend: `$env:LLM_PROVIDER='stub'; $env:DATABASE_URL='sqlite:///assistant_lab7_demo.db'; $env:API_ADMIN_KEY='lab7-demo-admin'; .\.venv\Scripts\python.exe -m uvicorn assistant_api.main:create_app --factory --host 127.0.0.1 --port 8000`
- UI: `$env:ASSISTANT_API_URL='http://127.0.0.1:8000'; .\.venv\Scripts\python.exe -m streamlit run ui/app.py --server.headless true --server.port 8501`

| Tình huống kiểm tra | Kết quả thực tế quan sát trên trình duyệt / API | Minh chứng |
|---|---|---|
| Màn hình đầu tiên & sidebar | Tiêu đề `🎓 FIT Study Assistant`, lời chào `WELCOME` nêu rõ AI assistant, sidebar có 4 câu mẫu và cảnh báo kiểm tra với Training Office, không báo lỗi backend. | [01_desktop_thesis_feedback.png](screenshots/01_desktop_thesis_feedback.png) |
| D.4 · Bấm câu ví dụ `Can I register my thesis with 118 credits?` | Gửi 1 cặp hỏi–đáp, trả điều kiện tối thiểu `120 accumulated credits` và `GPA of at least 2.0`, hiện `Sources: H26#5.3 — 5.3 Thesis registration` và panel Bonus `📚 Source details (1)`. | [01_desktop_thesis_feedback.png](screenshots/01_desktop_thesis_feedback.png) |
| D.4 · Bấm `👍 Helpful` và `👎 Not helpful` (F1) | Sau HTTP `201`, hiện `"Thanks for your feedback!"` (👍) và `"Thanks — we will look at this answer."` (👎), cả hai nút ẩn ngay lập tức; rerun không gửi lặp. | [01_desktop_thesis_feedback.png](screenshots/01_desktop_thesis_feedback.png), [02_desktop_escalation_down.png](screenshots/02_desktop_escalation_down.png) |
| D.4 · `what is the capital of France` | Không hiện `Sources:`, hiện ghi chú escalation `Training Office, room I.101`. | [02_desktop_escalation_down.png](screenshots/02_desktop_escalation_down.png) |
| `I lost my student card` & học phí | Trả lời `Student Affairs (room I.102)` kèm `S26#3 — 3 Student card replacement`; câu `Tuition for 18 credits and 2 retake` trả `9,450,000 VND`. | [03_desktop_card_tuition_validation.png](screenshots/03_desktop_card_tuition_validation.png) |
| D.4 · Nhập toàn khoảng trắng `"   "` | Hiện cảnh báo `"Please type a question."`, không gửi `POST /v1/chat`, giữ nguyên số tin nhắn trong lịch sử. | [03_desktop_card_tuition_validation.png](screenshots/03_desktop_card_tuition_validation.png) |
| D.4 · Dừng API rồi hỏi `"Where is the library?"` | Hiện banner mất kết nối ở đầu trang và tin nhắn `"⚠️ Cannot reach the assistant. Is the backend running?"`; lịch sử cũ vẫn giữ nguyên. | [05_desktop_backend_offline.png](screenshots/05_desktop_backend_offline.png) |
| Khởi động lại API với cùng `assistant_lab7_demo.db` & kiểm persistence | `GET /v1/feedback` (với `X-API-Key`) trước và **sau khi restart Uvicorn** đều trả đủ 2 bản ghi (`id=1`, `request_id=2084f000f0f2`, `rating=1`; `id=2`, `request_id=a30933798ad4`, `rating=-1`). Hỏi lại `"Where is the library?"` trên UI trả `Library: room B.201, open Mon-Sat 07:00-20:00.` và banner lỗi biến mất. | Log API + `test_api_feedback_sqlite_persistence_across_restart` |
| Hai tab & màn hình hẹp `375x812` | Tab 2 mở mới chỉ có lời chào ban đầu (cô lập session); tại `375x812`, sidebar thu gọn sạch, bong bóng chat, expander nguồn, nút 👍/👎 xếp gọn và ô nhập vẫn thao tác bình thường. | [04_mobile_375.png](screenshots/04_mobile_375.png) |

## 3. Hạng mục Bonus (+1 điểm) đã bổ sung

- **Hiển thị nguồn có cấu trúc (`ui/logic.py::source_items`, `ui/app.py::render_sources`):** Ngoài dòng `Sources:` chuẩn L1, các câu trả lời có tài liệu kèm theo expander `📚 Source details (N)` phân loại theo nhóm (`Student Handbook` cho `H26#`, `Campus Services` cho `S26#`, `Tuition & Fees` cho `F26#`).
- **Hiệu ứng chờ trực tiếp trong luồng chat (`ui/app.py`):** Khi người dùng gửi câu hỏi (qua ô chat hoặc sidebar), UI hiển thị ngay bong bóng người dùng và spinner `"Thinking… Checking official documents and tools…"` trong bong bóng trợ lý trong lúc chờ `/v1/chat`.
