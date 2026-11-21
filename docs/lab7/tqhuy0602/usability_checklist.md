# Lab 7 — Usability checklist của Huy

Kiểm ngày 21/11/2026 bằng Chrome và Playwright với Streamlit 1.39.0/FastAPI thật, desktop 1280×900 và viewport 375×812.
Đây là kiểm tra kỹ thuật của Codex, không phải buổi H1 với người ngoài nhóm.

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

| Mục | Minh chứng |
|---|---|
| 1, 8 | [Màn hình đầu](desktop-welcome.png), có giới hạn chức năng, ví dụ và thông báo AI |
| 2 | Browser gửi 2.001 ký tự/khoảng trắng không tạo POST; AppTest xác nhận cảnh báo và không crash |
| 3 | [Thinking… khi POST bị chậm](desktop-waiting.png), chỉ một request chat |
| 4 | [Thesis H26#5.3](desktop-thesis.png), [thẻ S26#3 tại 375 px](mobile-card-375.png); phép tính học phí không ép nguồn giả |
| 5 | [Thiếu căn cứ → Training Office I.101](desktop-escalation.png) |
| 6 | [Uvicorn dừng thật, UI giữ lịch sử và báo mất kết nối](desktop-backend-offline.png) |
| 7 | [201 và lời cảm ơn](mobile-feedback-saved.png), [lỗi 500 vẫn cho retry](mobile-feedback-retry.png); cả hai nút đều có AppTest |
| 9, 10 | [375 px](mobile-feedback-retry.png): nguồn xuống dòng, hai nút có nhãn chữ, không có cuộn ngang |

Chi tiết phép kiểm và request thực tế: [browser-results.json](browser-results.json), [log chạy](browser-smoke.txt).
