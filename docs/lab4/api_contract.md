# Lab04 — API contract (bài cá nhân Trần Quốc Huy)

| Method | Path | Input | Thành công | Lỗi trong phạm vi bài | Caller |
|---|---|---|---|---|---|
| GET | `/health` | Không | 200 `{status:"ok", version:"1.0.0"}` | — | Ops/UI |
| POST | `/v1/chat` | JSON `message`, `session_id?` | 200 `{answer,intent,sources,degraded,request_id}` | 422 `invalid_request` | UI/tests |
| POST | `/v1/feedback` | JSON `request_id`, `rating`, `comment?` | 201 `{id,created_at,request_id,rating,comment}` | 422 `invalid_request` | UI |
| GET | `/v1/feedback` | Header `X-API-Key` | 200 danh sách feedback trong app hiện tại | 401 `missing_or_invalid_api_key` | Staff dashboard |
| GET | `/v1/weather` | Không; tọa độ lấy từ Settings | 200 `{temperature_c,wind_kmh,description,observed_at,stale}` | 503 `weather_service_unavailable` nếu upstream lỗi và chưa có cache | UI |
| GET | `/v1/offices` | Không | 200 list `{name,room,hours}` sắp theo name từ core | — | UI |

`message` bắt buộc, là chuỗi 1–2000 ký tự và không toàn khoảng trắng.
`session_id` mặc định `anonymous`, tối đa 64 ký tự. `request_id` feedback dài 1–64;
`rating` là số nguyên -1/0/1; `comment` có thể bỏ qua/null, tối đa 500 ký tự.
`created_at` dùng UTC. Feedback chỉ ở RAM, mất khi khởi động lại ứng dụng.

Lỗi validation/auth/weather có dạng `{"error":{"code":"...","message":"..."}}`.
Route không tồn tại giữ hành vi framework: 404 `{"detail":"Not Found"}`.
Rate limiting là bonus chưa bật; không nhận đã hoàn thành bonus.

UI nên chỉ rõ input cần sửa khi nhận 422, yêu cầu admin đăng nhập/kiểm tra key khi 401,
và báo thời tiết tạm không có khi 503. Với 200 `stale=true`, vẫn hiển thị dữ liệu nhưng
đánh dấu là bản cũ kèm `observed_at`.
Đổi tên/xóa trường bắt buộc hoặc đổi kiểu/schema đang dùng cần cân nhắc `/v2`;
thêm endpoint độc lập hoặc trường tùy chọn thường vẫn tương thích `/v1`.
