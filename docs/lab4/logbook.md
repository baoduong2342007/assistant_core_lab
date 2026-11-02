# Lab04 Logbook — Phan Quỳnh Quyền

## 2026-11-02

- Khởi tạo nhánh `feat/lab04-pqquyenn` từ `origin/main`.
- Hoàn thành bài warm-up P1–P5 (`practice/hello_api.py`), kiểm tra 5/5 test pass với `practice/test_hello_api.py`.
- Triển khai toàn bộ các endpoint T1–T4 trong `src/assistant_api/main.py`:
  - `POST /v1/chat`: kết nối core `AssistantService`, trả `ChatResponse` kèm `request_id`.
  - `POST /v1/feedback` và `GET /v1/feedback`: lưu trữ phản hồi và phân quyền admin.
  - `GET /v1/weather`: tích hợp client Open-Meteo, xử lý lỗi ngoại vi và cache fallback.
- Thực hiện bài tập H1 (chuyên trách): thêm `OfficeDirectory.all()` sắp xếp văn phòng theo tên, thêm endpoint `GET /v1/offices`, viết 2 test case xác nhận danh sách sắp xếp và có sự hiện diện của "Library".
- Kích hoạt Part F Chat Rate Limiting theo địa chỉ IP của client, trả mã lỗi 429 khi vượt ngưỡng `RATE_LIMIT_PER_MIN`.
- Viết 14 test cases xử lý lỗi ngoại vi weather trong `tests/test_weather_validation.py`.
- Chạy kiểm thử toàn bộ hệ thống: 240/240 tests passed, 5/5 practice tests passed.
- Kiểm tra mã nguồn với Ruff (`check`, `format --check`, `check --select BLE`) đạt 100%.
- Chạy thực nghiệm curl test lưu tại `docs/lab4/pqquyenn/curl_tests.log`.
- Soạn thảo H2 reflection 5 dòng và API contract tại `docs/lab4/api_contract.md`.
- Thực hiện peer review cho PR #41 của Trần Quốc Huy tại `docs/lab4/pqquyenn/review-huy.md`.
