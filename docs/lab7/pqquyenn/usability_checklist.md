# Lab 7 — Usability checklist (tick before your user test)

Đã kiểm tra thực tế trên bản chạy local (FastAPI `stub` + Streamlit `1.39.0`) với trình duyệt ở kích thước desktop `1280x800`, màn hình hẹp `375x812`, hai tab độc lập và bộ kiểm thử `AppTest`. Xem chi tiết tại [demo_results.md](demo_results.md).

- [x] The first screen says what the assistant can do, with example questions
- [x] Empty or too-long input shows a friendly message (not a crash)
- [x] While waiting, the user sees "Thinking…"
- [x] Every answer from documents shows its sources
- [x] "I don't know" answers tell the user who can help (escalation)
- [x] If the backend is down, the page says so clearly
- [x] Each answer has 👍 / 👎, and clicking gives a "thanks" message
- [x] The page says it is an AI assistant
- [x] Text is readable (size, contrast); buttons have clear labels
- [x] Works on a phone-width window

Ghi chú kiểm chứng: trong trình duyệt local với backend stub phản hồi nhanh, chữ `"Thinking…"` thoáng qua nhanh trong lúc chờ rerun; trạng thái hiển thị `"Thinking…"` đã được xác nhận trong mã `ui/app.py` (`with st.spinner("Thinking…")`). Buổi test 10 phút với người ngoài nhóm xem tại [user_test_observations.md](user_test_observations.md).
