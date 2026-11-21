# D.4 — Minh chứng UI/HTTP thật của Huy

Ngày 21/11/2026; Chrome headless, Streamlit 1.39.0, backend nhóm với stub và SQLite tạm riêng.
Runner dùng wrapper [demo_api.py](demo_api.py) để ghi các request tổng hợp, tạo chậm và mô phỏng lỗi HTTP/provider có kiểm soát; lệnh dừng/restart Uvicorn dùng tiến trình thật và cùng file DB.
Các sửa UI và API client nằm trong repo; wrapper không được dùng ở entry point production.

| Tình huống | Kết quả quan sát | Minh chứng |
|---|---|---|
| Sidebar + chờ | Một POST cho câu mẫu; có Thinking… trong lúc chờ | [waiting](desktop-waiting.png) |
| Thesis 118 credits | Đoạn trả lời giữ điều kiện 120 credits và GPA 2.0; nguồn H26#5.3 | [thesis](desktop-thesis.png) |
| Capital of France | API abstain, sources rỗng; UI hiện Training Office I.101 | [escalation](desktop-escalation.png) |
| Trống/quá dài | Khoảng trắng và 2.001 ký tự không tạo POST; AppTest kiểm cảnh báo cho cả hai | browser trace + [UI tests](ui-tests.txt) |
| 👍 | POST rating=1 và đúng request_id; HTTP 201 → cảm ơn, ẩn cả hai nút | browser trace, AppTest cho hai hướng đánh giá |
| 👎 bị lỗi rồi retry | HTTP 500 không đánh dấu đã gửi; nút còn dùng được; retry 201 → cảm ơn và ẩn nút | [retry](mobile-feedback-retry.png), [saved](mobile-feedback-saved.png) |
| Feedback 404 | Client chỉ dẫn hỏi lại; AppTest giữ nút và cho retry thành công | MockTransport + AppTest |
| API dừng rồi chạy lại | UI báo mất kết nối, vẫn đọc được lịch sử; câu mới chạy lại được, session_id giữ nguyên | [offline](desktop-backend-offline.png), [recovered](desktop-recovered-fee.png) |
| Thẻ sinh viên | Student Affairs I.102, 50,000 VND, 3 working days và S26#3 | [375 px](mobile-card-375.png) |
| Học phí | 18 credits + 2 retake → 9,450,000 VND, sources rỗng | [fee](desktop-recovered-fee.png) |
| Provider lỗi | Hai lần stub thất bại → retrieval với degraded=true, nguồn S26#3 và ghi chú | [fallback](desktop-fallback.png) |
| Timeout/422/429/500, health lỗi | Thông báo riêng, có bước xử lý; không crash hoặc tự gửi lại POST | MockTransport trong `tests/test_lab7_huy_client.py` |
| Hai phiên / 375 px | session_id hai browser context khác nhau; một phiên giữ ID qua rerun; nguồn xuống dòng, nhãn rõ, không cuộn ngang | [trace/viewport](browser-results.json), [checklist](usability_checklist.md) |
| Persistence | Sau restart cùng DB, đọc lại được đúng hai feedback thành công với rating -1 và 1 | `feedback_after_restart` trong browser-results.json |

[browser-results.json](browser-results.json) lưu status, payload và response của HTTP; [browser-smoke.txt](browser-smoke.txt) là log runner.
Đây là dữ liệu kiểm thử tổng hợp, không phải dữ liệu sinh viên thật hoặc quan sát người dùng thật.

## Chạy lại

Cần Node.js, Chrome và Playwright; chạy tại root repo, trong venv đã cài requirements.

```bash
npm install --prefix /tmp/lab07-browser playwright
NODE_PATH=/tmp/lab07-browser/node_modules node docs/lab7/tqhuy0602/browser-smoke.cjs
```

Mặc định runner dùng Chrome tại `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`; đặt `CHROME_PATH` nếu máy khác.
Runner dùng hai cổng 18701/18702, tạo SQLite/trace trong thư mục tạm và dừng các tiến trình của nó khi kết thúc.
Không chạy wrapper demo trên dịch vụ dùng chung vì nó ghi câu hỏi tổng hợp và có công tắc lỗi phục vụ kiểm thử.
