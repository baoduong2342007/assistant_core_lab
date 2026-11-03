# Lab 4 — API Contract Worksheet

| Method | Path | Request body / params | Success (code + body) | Errors (code + error.code) | Who calls it |
|---|---|---|---|---|---|
| GET | `/health` | — | 200 `{"status": "ok", "version": "1.0.0"}` | — | ops, UI |
| POST | `/v1/chat` | `{"message": str, "session_id": str}` | 200 `{"answer", "intent", "sources", "degraded", "request_id"}` | 422 `invalid_request`, 429 `too_many_requests` | UI, tests |
| POST | `/v1/feedback` | `{"request_id": str, "rating": int, "comment": str}` | 201 `{"id", "request_id", "rating", "comment", "created_at"}` | 422 `invalid_request` | UI |
| GET | `/v1/feedback` | header `X-API-Key: <key>` | 200 `list[FeedbackOut]` | 401 `missing_or_invalid_api_key` | staff dashboard |
| GET | `/v1/weather` | — | 200 `{"temperature_c", "wind_kmh", "description", "observed_at", "stale"}` | 503 `weather_service_unavailable` | UI |
| GET | `/v1/offices` | — | 200 `list[Office]` sorted by name | — | UI, tests |

### Questions

**1. Which fields are required, and what are their limits?**
* `/v1/chat`: `message` là bắt buộc, chuỗi từ 1 đến 2000 ký tự (không được là chuỗi rỗng hoặc toàn khoảng trắng). `session_id` là tùy chọn, mặc định `"anonymous"`, tối đa 64 ký tự.
* `/v1/feedback`: `request_id` là bắt buộc, chuỗi từ 1 đến 64 ký tự; `rating` là số nguyên trong khoảng [-1, 1] (-1: không hài lòng, 0: trung lập, 1: hài lòng); `comment` là tùy chọn (hoặc null), chuỗi tối đa 500 ký tự.

**2. What does the UI show for each error code?**
* `401`: Hiển thị thông báo "Yêu cầu quyền quản trị viên. Vui lòng kiểm tra lại API Key".
* `422`: Hiển thị lỗi kiểm thực dữ liệu chi tiết ngay dưới trường nhập liệu (ví dụ: "Tin nhắn không được để trống", "Đánh giá chỉ từ -1 đến 1").
* `429`: Hiển thị cảnh báo "Bạn đang gửi yêu cầu quá nhanh. Vui lòng thử lại sau 1 phút".
* `503`: Hiển thị thông báo "Dịch vụ thời tiết hiện tạm thời không khả dụng, vui lòng thử lại sau".

**3. What changes would force a `/v2`?**
* Các thay đổi làm phá vỡ tính tương thích ngược (breaking changes) như:
  * Đổi tên hoặc xóa các trường bắt buộc trong request/response (ví dụ đổi `message` thành `prompt` hoặc `answer` thành `content`).
  * Thay đổi kiểu dữ liệu (ví dụ đổi `rating` từ integer sang float/string).
  * Thay đổi cấu trúc lỗi (error shape) hoặc cách thức xác thực header.
