# Lab 7 homework — 10-minute usability test

Tester (not in your team, first name only): PENDING (cần người ngoài nhóm test 10 phút)  Date: PENDING
Task you gave them: "Find out if you can register your thesis with 118 credits, and where to replace a lost student card."

Rule: do not help or explain. Watch and write down what happens.

| # | What the tester did or said | What they expected | Why the system/UI caused it | Fix idea |
|---|---|---|---|---|
| 1 | PENDING | PENDING | PENDING | PENDING |
| 2 | PENDING | PENDING | PENDING | PENDING |
| 3 | PENDING | PENDING | PENDING | PENDING |

The one change we made (commit link): PENDING (sẽ cập nhật sau khi có 3 quan sát thật từ người thử ngoài nhóm)
Before / after screenshot: PENDING

## Ghi chú tự kiểm tra UI trước khi mời người thử

- Tài liệu này chưa ghi nhận quan sát từ người thật ngoài nhóm; các kiểm tra trình duyệt đã chạy ở [demo_results.md](demo_results.md) là kiểm thử kỹ thuật tự động trên Chrome.
- Một điểm nhỏ ghi nhận trong quá trình thử ô nhập: khi nhấn Enter lúc ô chat trống trên một số môi trường webview, textarea của Streamlit có thể giữ lại một ký tự xuống dòng (`"\n"`); `validate_input()` vẫn chặn hợp lệ không gửi `POST /v1/chat`, nhưng có thể cân nhắc bổ sung chỉ dẫn ngắn hoặc kiểm tra thêm khi người ngoài nhóm trải nghiệm thực tế.
