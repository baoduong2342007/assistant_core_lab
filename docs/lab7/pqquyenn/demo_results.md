# Lab 07 — Kết quả kiểm thử D.4 và trình duyệt thật (`pqquyenn`)

Chạy thực tế hai server tại root repo:
- Backend: `LLM_PROVIDER=stub`, `DATABASE_URL=sqlite:///assistant_lab7_quyen_demo.db`, `python -m uvicorn assistant_api.main:create_app --factory --host 127.0.0.1 --port 8000`
- Frontend: `ASSISTANT_API_URL=http://127.0.0.1:8000`, `python -m streamlit run ui/app.py --server.headless true --server.port 8501`

File SQLite demo đã được xóa sau khi kiểm tra để không lọt vào commit; phần kiểm chứng persistence qua restart được kiểm tra lặp lại tự động trong `tests/test_lab7_quyen_ui.py::test_kb_answers_degraded_fallback_and_sqlite_persistence`.

## Kết quả các tình huống D.4 và ma trận mục 5

| Tình huống | Kết quả quan sát thực tế trên trình duyệt / test | Minh chứng |
|---|---|---|
| Màn hình đầu (`1280x800`) | Hiển thị tiêu đề `🎓 FIT Study Assistant`, lời chào giới thiệu phạm vi + vai trò AI, 4 nút câu mẫu ở sidebar, nút `New chat` và không có banner lỗi kết nối. | `GET /health` trả `200 OK` |
| D.4 · Bấm câu ví dụ `Can I register my thesis with 118 credits?` | Gửi 1 `POST /v1/chat` (`200 OK`), trả lời tối thiểu 120 tín chỉ và GPA 2.0, kèm `Sources: H26#5.3 — 5.3 Thesis registration` và hai nút `👍 Helpful` / `👎 Not helpful`. | [desktop_offline_history_preserved.png](screenshots/desktop_offline_history_preserved.png) |
| Câu cấp lại thẻ `I lost my student card` + bấm 👍 | Trả lời `Student Affairs (room I.102)`, phí `50,000 VND`, `3 working days`, kèm `Sources: S26#3 — 3 Student card replacement`. Bấm `👍 Helpful` gửi `POST /v1/feedback` (`201 Created`), hiện `Thanks for your feedback!` và ẩn cả hai nút. | [desktop_card_escalation_feedback.png](screenshots/desktop_card_escalation_feedback.png) |
| D.4 · `what is the capital of France` + bấm 👎 | `path=abstain`, `escalate=true`, không có dòng `Sources:`, hiện thông báo `I could not find this in the official documents. A staff member can help: Training Office, room I.101.`. Bấm `👎 Not helpful` gửi `POST /v1/feedback` (`201 Created`), hiện `Thanks — we will look at this answer.` và ẩn hai nút. | [desktop_card_escalation_feedback.png](screenshots/desktop_card_escalation_feedback.png) |
| D.4 · Enter ô trống và chuỗi chỉ có khoảng trắng (`"   "`) | Ô trống + Enter không gửi `POST /v1/chat`. Nhập `"   "` hiện cảnh báo vàng `Please type a question.` và log Uvicorn không có request `POST /v1/chat` mới. Input `> 2000` ký tự được kiểm qua `AppTest` và `validate_input`. | [desktop_card_escalation_feedback.png](screenshots/desktop_card_escalation_feedback.png) · `tests/test_lab7_quyen_ui.py` |
| Học phí `Tuition for 18 credits and 2 retake` ở `375x812` | Trả về `Your tuition is 9,450,000 VND.`, không có dòng `Sources:`. Ở `375x812`, sidebar thu gọn sạch, chữ xuống dòng gọn (`body` rộng `375.33px`, khung trả lời `215.33px`, chat input `336px`), hai nút `👍 Helpful` / `👎 Not helpful` xếp dọc vừa khít không tràn ngang. | [mobile_375_tuition_buttons.png](screenshots/mobile_375_tuition_buttons.png) |
| Hai tab trình duyệt độc lập | Tab 2 mở `http://localhost:8501` chỉ có 1 lời chào ban đầu (`userMessages = 0`), tách biệt hoàn toàn với lịch sử của Tab 1. | `tests/test_lab7_quyen_ui.py` + kiểm thử trình duyệt |
| D.4 · Dừng API rồi hỏi `Where is the library?` | Sau khi tắt Uvicorn, UI hiện banner đỏ `The assistant backend is unreachable. Your chat history is kept here; start or restart the API server and try again.` và thông báo `⚠️ Cannot reach the assistant backend...`, vẫn đọc được toàn bộ lịch sử trước đó. | [desktop_offline_history_preserved.png](screenshots/desktop_offline_history_preserved.png) |
| D.4 · Khởi động lại API với cùng SQLite DB và hỏi `Where is the library?` | Banner lỗi biến mất, trả về `Library: room B.201, open Mon-Sat 07:00-20:00.` (không có `Sources:`), các xác nhận feedback cũ giữ nguyên và log Uvicorn đợt 2 không bị gửi lại `POST /v1/feedback`. | [desktop_recovered_library.png](screenshots/desktop_recovered_library.png) |
| `degraded=true`, timeout, `429`, `500`, feedback `404` và persistence SQLite | Kiểm qua `MockTransport`, `AppTest` và hai instance `create_app` trên cùng file SQLite tạm (`GET /v1/feedback` đọc lại được bản ghi sau restart). | `tests/test_lab7_quyen_ui.py` |
