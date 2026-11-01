# Review hỗ trợ cho Huy — bản Lab04 của Dương

Đối tượng: PR #36, branch `feat/lab04-baoduong2342007`, commit
`2a4f269ff32f1db5913b35b73e289cf5549bd5f4`, kiểm tra ngày 01/11/2026.
Đây là nhận xét kỹ thuật do Codex hỗ trợ Huy, **chưa gửi GitHub review và không phải human approval**.

## Phát hiện có thể tái hiện

**[P2] Validate JSON upstream trước khi đọc `current`.** Tại
`src/assistant_api/weather.py:62–71`, code truy cập `r.json()["current"]` và các field con
trước khi xác nhận cấu trúc. Upstream 200 với `[]`, `{"current":null}` hoặc `{"current":[]}`
ném TypeError nằm ngoài nhóm catch. Endpoint hiện trả 500 thay vì retry/fallback và 503 khi chưa cache.
Nếu đã có cache cũ, lỗi cấu trúc này cũng bỏ qua nhánh trả `stale=true`.

Đã chạy chính code candidate qua PYTHONPATH từ bản `git archive`, với MockTransport và
`TestClient(..., raise_server_exceptions=False)`, retries=0 để minh họa trực tiếp:

| Body upstream HTTP 200 | GET `/v1/weather` thực tế |
|---|---|
| `[]` | 500 `Internal Server Error` |
| `{"current":null}` | 500 `Internal Server Error` |
| `{"current":[]}` | 500 `Internal Server Error` |
| `{}` | 503 `weather_service_unavailable` (KeyError đã được catch) |

Đề xuất: validate upstream bằng model/schema hoặc kiểm tra kiểu rõ ràng rồi chuyển lỗi dữ liệu
vào luồng ExternalServiceError; bổ sung tests chưa cache và cache hết TTL. Bản của Huy đã có
model `_Forecast`/`_CurrentWeather` và các trường hợp tương ứng trong `tests/test_weather.py`.

## Phần đã đối chiếu

Factory dùng core nhóm, T1 giữ các field Response và request_id; admin key nằm trong Settings
và bị loại khỏi repr/serialization; timeout/coordinates được đọc từ env. Không có kết luận
approval tổng thể, không ghi reviewer khác đã duyệt và không tự merge candidate.
