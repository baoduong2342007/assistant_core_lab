# Trần Quốc Huy (`tqhuy0602`) — Lab04

Ngày thực hiện: 01/11/2026 (Asia/Ho_Chi_Minh). Nhánh: `feat/lab04-tqhuy0602`.
Base main: `fc103c7572b487c3fc47706c88af00330876dda7`.
Theo dõi: [Issue #40](https://github.com/baoduong2342007/assistant_core_lab/issues/40).
Huy đã cho phép push code/tests/tài liệu/ảnh minh chứng và tạo draft PR ngày 01/11/2026.

## Phần đã thực hiện với Codex

- [x] P1–P5 trong `practice/`; 5 tests đạt.
- [x] T1–T4 bọc core nhóm tuần 3; giữ các cải tiến CLI/knowledge và toàn bộ test cũ.
- [x] CL-H: Settings/env/.env.example, admin-key wiring, validation và bảo vệ key.
- [x] HW-H: test env precedence/defaults/invalid values; weather success/error/retry/fresh/stale/recovery.
- [x] H1 cá nhân: `OfficeDirectory.all()`, GET `/v1/offices`, hai test API, dữ liệu từ core thật.
- [x] Contract, hướng dẫn chạy và [weather checks](weather-checks.md).
- [x] Đã chạy curl thật, đối chiếu mã status trong [log](curl-results.txt).
- [x] [Ảnh Swagger](swagger-chat.png) là request POST `/v1/chat` thực sự với session `tqhuy0602-lab04`, trả 200.
- [x] H2 có [bản nháp đúng 5 dòng do AI hỗ trợ](reflection.md).
- [x] Có [nhận xét review hỗ trợ PR36](review-duong.md), tái hiện lỗi weather JSON sai cấu trúc; chưa gửi review thay Huy.

## Kiểm tra local đã chạy

Python 3.11.16, macOS; venv theo `requirements.txt` của Lab04 (FastAPI 0.115.0,
Pydantic 2.9.2, HTTPX 0.27.2, uvicorn 0.30.6, pytest 8.3.3, Ruff 0.6.9).
Baseline main: **212 passed**. Sau thay đổi:

| Lệnh từ root repo | Kết quả |
|---|---|
| `.venv/bin/python -m pytest -q` | 274 passed, 1 skipped (bonus rate limit) |
| `.venv/bin/python -m pytest -q practice/` | 5 passed |
| `.venv/bin/python -m pytest -q tests/test_config.py tests/test_weather.py tests/test_api_huy.py` | 78 passed |
| `.venv/bin/python -m ruff check .` | Passed |
| `.venv/bin/python -m ruff format --check .` | Passed |
| `.venv/bin/python -m ruff check --select BLE .` | Passed |
| `.venv/bin/python -m pip check` | No broken requirements |

Có một DeprecationWarning từ Starlette 0.38.6/AnyIO trong bộ thư viện cài theo requirements;
không làm test thất bại. CI Python 3.10/3.12 được theo dõi riêng, không suy từ test local.
Workflow CI hiện có đã thêm lệnh chạy riêng `practice/`, vì root pytest chỉ thu thập `tests/`.

Curl chính thức: 200 health/chat fee/chat rule/weather; 201 tạo feedback;
422 chat rỗng/sai kiểu/rating sai; 401 đọc feedback thiếu key;
200 đọc feedback đúng key; 404 route lạ với shape mặc định framework.
Đã assert cả 11 status trong log và kiểm tra thêm offices/whitespace/key sai, lưu
[kết quả bổ sung](manual-extra-results.json).
Weather curl dùng Open-Meteo thật; các tình huống 503/stale được kiểm tra bằng transport giả trong pytest.

## Những xác nhận cá nhân/nhóm còn lại

- [ ] Huy đọc và tự diễn đạt/xác nhận H2; không coi bản nháp AI là lời tự viết đã xác nhận.
- [ ] Review bản của Dương theo vòng phân công; chưa có peer approval do Huy thực hiện.
- [ ] Quyền review phần config/weather của Huy; chưa nhận là đã có approval.
- [ ] Nộp link PR lên LMS và xác nhận hạn ngày trước Lab05 (chưa có ngày Lab05).
- [ ] Nhóm chọn candidate API, review/merge và tạo tag `v0.4-api`; không thuộc thao tác tích hợp của Huy.

Không ghi giờ cá nhân, attendance, peer approval hoặc nộp LMS khi chưa có xác nhận từ người học.

## Nguồn và AI use

Scaffold/API schemas/weather/ratelimit, 5 practice tests, test API mẫu và curl/Postman lấy từ
`CSC10014-at-fit-hcmus/public_materials` commit `a848a96d44876d4baee5eabe645114cf56d0b82f`, thư mục `lab04/`.
Giữ core của repo nhóm; không chép core starter và không ghi đè `tests/conftest.py`.
Tests API mẫu được thích nghi bằng fixture cục bộ và cleanup client, giữ skip bonus, thêm hai test H1.
Ruff chỉ chuẩn hóa trình bày của practice tests mẫu; không đổi assertions.

Codex hỗ trợ toàn bộ code/tests/docs, chạy kiểm tra, thao tác Git và tạo minh chứng Swagger/curl.
Reflection là nháp AI; không xác nhận thay Huy việc tự học, diễn đạt hay review.
Xem thêm [AI-use log](../../ai-use-log.md).
