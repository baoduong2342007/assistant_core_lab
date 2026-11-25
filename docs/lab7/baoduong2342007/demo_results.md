# Lab 7 — D.4 và bàn giao của Dương

Kiểm ngày 25/11/2026 với Python 3.12.14 trên Windows, Chrome, Streamlit 1.39.0, FastAPI dùng stub và SQLite tạm. Mốc Lab 06 là `fe0d569`. Lượt kiểm D.4 dùng Playwright chuyển từ kịch bản của Huy. Dữ liệu demo và câu hỏi đều là mẫu.

| Tình huống | Kết quả thực tế |
| --- | --- |
| Bấm câu ví dụ ở sidebar | Hiện câu hỏi cùng dòng “Thinking…” bên dưới, gửi đúng một POST và hiển thị đúng một đáp án. [Đang chờ](desktop-waiting.png) |
| Hỏi về khóa luận với 118 tín chỉ | Hiện yêu cầu tối thiểu 120 tín chỉ và GPA 2.0, nguồn `H26#5.3`. [Khóa luận](desktop-thesis.png) |
| Hỏi thủ đô nước Pháp | API trả `abstain` và danh sách nguồn rỗng. UI chỉ tới Phòng Đào tạo I.101. [Escalation](desktop-escalation.png) |
| Enter với ô trống | Không có POST. Chuỗi khoảng trắng và chuỗi 2.001 ký tự cũng không tạo POST. AppTest xác nhận cảnh báo khi chuỗi không hợp lệ đi tới validate. |
| Bấm 👍 và 👎 trên hai câu | Cả hai lần thành công nhận HTTP 201 với đúng ID và rating. Nút ẩn sau khi thấy lời cảm ơn. Feedback 👎 gặp HTTP 500 vẫn có thể bấm lại và lưu được. Lượt rerun không gửi thêm vote. [Feedback đã lưu](mobile-feedback-saved.png) |
| Dừng API rồi gửi câu hỏi | UI báo mất kết nối và giữ lịch sử. Sau khi API khởi động lại, cùng tab trả phí 9.450.000 VND và giữ `session_id`. File SQLite vẫn chứa hai vote trước đó. [API mất kết nối](desktop-backend-offline.png) |
| Cấp lại thẻ, fallback, và hai phiên UI | Thẻ sinh viên hiển thị I.102, nguồn `S26#3`. Provider lỗi có thông báo trả lời trực tiếp từ tài liệu. Hai phiên có ID riêng và giao diện 375 px không tràn ngang. [Màn hình 375 px](mobile-card-375.png) |

## Kết quả kiểm thử

| Kiểm tra | Kết quả |
| --- | --- |
| Starter chính thức `ea80fc9` | Warm-up 1 đạt, 3 TODO chưa đạt. Suite UI 5 đạt, L1/L2 chưa đạt. |
| Warm-up U1–U4 từ thư mục `practice` | 4/4. |
| Bảy test UI gốc | 7/7. |
| Toàn bộ pytest ở thư mục gốc | 580 đạt. Có một cảnh báo deprecation từ Starlette/AnyIO. |
| Practice cũ và warm-up | 18/18. SQL đạt 15/15. |
| Ruff lint, format, BLE | Cả ba đạt. |
| Lab 06 | CLI stub trả chỉ dẫn I.102. Retrieval và LLM stub đạt 20/20 và 45/45 trên hai bộ eval. |
| Clone sạch | Tạo venv mới và cài đủ dependencies theo README. FastAPI và Streamlit báo health 200. Hỏi về cấp lại thẻ qua API trả I.102 và `S26#3`. |

## Bàn giao

- Bản tích hợp dùng HTTP client của Huy; lấy kiểm thử SQLite và gate rà conflict trong `ui/` từ Minh. Git ghi tác giả commit nền của Huy. Dương phụ trách ghép luồng chat, hiển thị trạng thái chờ trong lịch sử và hướng dẫn chạy hai terminal.
- Codex hỗ trợ hiện thực, xác minh và soạn bản nháp H2. Buổi thử 2 phút và H1 cần người ngoài nhóm. Mẫu H1 đã có nhiệm vụ và chỗ ghi ba quan sát. Tiến độ H2 cá nhân cần Dương tự đọc hai chương và xác nhận hai câu.
- Sau khi peer duyệt bản tích hợp và CI đạt trên Python 3.10/3.12, merge qua GitHub, kiểm `main` sau merge rồi tạo `v0.7-mvp` trên đúng SHA. Đối chiếu hạn trên LMS trước khi Tech Lead nộp link tag và từng thành viên nộp link PR. Tag `v0.6-ai` chưa xuất hiện trên remote khi kiểm.
