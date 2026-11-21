# Lab 07 — bàn giao Trần Quốc Huy (`tqhuy0602`)

Ngày 21/11/2026, Asia/Ho_Chi_Minh. Nhánh `feat/lab07-personal-tqhuy0602` từ main `fe0d569415c2c29317e99cc1d73d4d21425fbdf2`, đúng mốc của kế hoạch.
Code commit: `fc655896137476e28ff208ebd5c29f479342230b`.
Học liệu: `CSC10014-at-fit-hcmus/public_materials` tại `ea80fc97f747cadecde2262c9fd934eb2393c082`, thư mục `lab07`.
[Provenance và hash file](provenance.json) phân biệt starter và phần hoàn thành.

## Phạm vi tích hợp của Huy

- `ui/api_client.py` giữ contract `ChatResult`, `ask`, `send_feedback -> bool`, `healthy -> bool`; không import core hoặc gọi service trực tiếp.
- `ASSISTANT_API_URL` đọc từ process chạy UI, mặc định `http://127.0.0.1:8000`; validate URL, hỗ trợ prefix reverse proxy, chặn URL sai/credentials/query/fragment; không tự đọc `.env` của backend.
- HTTP client có MockTransport injection, timeout mặc định 20 giây và health tối đa 2 giây, đóng kết nối sau mỗi rerun; không tự retry POST.
- Chat xử lý timeout, mất kết nối, 422, 429, 500/503 và JSON/schema sai; phản hồi lỗi có bước tiếp theo, không chép body lỗi upstream.
- Feedback chỉ thành công khi HTTP 201; `last_feedback_error` cung cấp lời nhắc cụ thể cho 404/422/429/server/mạng/timeout, giữ thao tác retry và xóa lỗi sau lần thành công.
- Giữ đầy đủ sources, path, escalate, degraded, confidence, intent và request_id; kiểm schema ở ranh giới HTTP thay vì để UI crash.
- README có hai terminal, giải thích vị trí đặt biến UI; test Lab 06 đổi so sánh chuỗi đường dẫn thành `Path` để xử lý dấu phân cách Windows.

## Bài cá nhân đã làm

- U1 giữ tiêu đề gốc; U2 chào tên; U3 session_state đếm được hai lần; U4 báo advisor khi >30 và tải bình thường khi ≤30.
- L1 hiện ID + title thật của nguồn; nguồn rỗng trả chuỗi rỗng; L2 xét escalation I.101 trước degraded, gồm trường hợp cả hai cờ true.
- F1 và 👍 dùng request_id tương ứng; chỉ xác nhận/khóa đánh giá sau 201, giữ nút nếu lỗi, không gửi lại khi rerun.
- Hai điểm nhập đi qua cùng validate/strip/spinner/HTTP, mỗi lượt một POST; session_id và lịch sử giữ qua rerun, hai phiên độc lập.
- [Checklist usability](usability_checklist.md) đủ 10 mục dựa trên kiểm tra thực tế, có ảnh desktop/375 px.
- [D.4](demo_results.md) có browser trace, ảnh và kiểm Uvicorn restart trên cùng SQLite; đọc lại được cả hai feedback đã lưu.
- `streamlit==1.39.0` trong requirements; optional extra `ui` trong pyproject; `tests/test_ui.py` được pytest chính thu thập; CI thêm 4 AppTest warm-up và giữ các gate cũ.

Đây là PR bài cá nhân nên có cả app/logic/warm-up; phạm vi để nhóm chọn tích hợp của Huy là client/config/test HTTP và sửa assertion đường dẫn.
Chưa có PR UI của Dương tại mốc bắt đầu để review độc lập; không tự nhận đã peer-approve phần của người khác.

## Kiểm chứng

Python local 3.11.16, pytest 8.3.3, Streamlit 1.39.0, macOS arm64.

| Gate | Kết quả |
|---|---|
| Starter gốc trước khi làm | UI 5 pass/2 fail, warm-up 1 pass/3 fail |
| `python -m pytest -q` | 579 passed: gồm 512 test cũ và 67 test UI mới |
| 7 test UI của đề | 7 passed, assertions được giữ |
| Client + AppTest bổ sung | 60 passed: 50 test client và 10 test app/logic |
| 4 AppTest warm-up, chạy trong practice và từ root | 4 passed ở mỗi cách chạy |
| Practice Lab 04/05/06 | 14 passed |
| SQL checker | 15/15 |
| Lab 06, 45 câu | retrieval/stub 45/45; deterministic giữ 17/45 |
| Ruff lint / format | Đạt |
| Chrome + hai server | Sidebar, nguồn, feedback, retry, offline/recover, hai phiên, spinner, 375 px và persistence đạt |

Log: [starter-before.txt](starter-before.txt), [tests.txt](tests.txt), [ui-tests.txt](ui-tests.txt), [warmup-tests.txt](warmup-tests.txt), [warmup-root-tests.txt](warmup-root-tests.txt), [browser-smoke.txt](browser-smoke.txt).
Một warning pytest đến từ deprecated alias của dependency Starlette/AnyIO.
Sửa `Path` đã qua suite local; không mô tả lần chạy macOS thành bằng chứng chạy Windows.

## H1/H2 và trạng thái nộp

**H1 chưa hoàn thành:** cần người ngoài nhóm thử thật 10 phút, ba quan sát, một fix dựa trên quan sát và cặp ảnh trước/sau cùng điều kiện.
[user_test_observations.md](user_test_observations.md) có kịch bản và chỗ điền; chưa có tên/ngày/thời lượng/quan sát để báo cáo.
Kiểm thử trình duyệt tự động và ảnh D.4 không được thay thế thành buổi thử người dùng.

**H2:** [reading.md](reading.md) có đúng hai câu, một ý đã áp dụng trong UI và một ý muốn thêm, trỏ tới hai chương PAIR.
Codex đã đọc nguồn và soạn nội dung; không xác nhận thay cho Huy rằng Huy đã tự đọc đủ 15 phút.

Codex hỗ trợ toàn bộ code, test, đọc nguồn, tài liệu và ảnh kiểm chứng trong lần làm này.
PR giữ dạng draft để bổ sung H1; chưa có peer review của Quyền, chưa nộp LMS hoặc tạo tag `v0.7-mvp`.
Không yêu cầu người dùng duyệt lại các bước code/test đã được giao; phần còn thiếu là dữ liệu của buổi H1 thật và các bước nhóm/LMS ngoài phạm vi hiện có.
