# Huy — cấu hình, admin key và weather

## Settings và biến môi trường

Giữ quy tắc tuần 3: defaults < `.env` < environment đã có. `load_settings(None)` bỏ qua `.env`.
Mọi cấu hình core cũ vẫn được kiểm thử. `api_admin_key` và `llm_api_key` bị loại khỏi repr,
`model_dump()` và JSON serialization; lỗi config chỉ nêu tên field, không in giá trị env.

| Environment | Field | Mặc định / validation |
|---|---|---|
| `API_ADMIN_KEY` | `api_admin_key` | None; thiếu/rỗng tắt truy cập admin; chuỗi chỉ có whitespace bị từ chối |
| `WEATHER_URL` | `weather_url` | Open-Meteo forecast; HTTP(S), không credentials/fragment |
| `WEATHER_TIMEOUT_S` | `weather_timeout_s` | 3; hữu hạn, > 0 |
| `WEATHER_RETRIES` | `weather_retries` | 1; nguyên, >= 0 |
| `WEATHER_CACHE_TTL_S` | `weather_cache_ttl_s` | 600; hữu hạn, >= 0; 0 buộc refresh |
| `CAMPUS_LAT` | `campus_lat` | 10.7626; hữu hạn, [-90, 90] |
| `CAMPUS_LON` | `campus_lon` | 106.6822; hữu hạn, [-180, 180] |
| `RATE_LIMIT_PER_MIN` | `rate_limit_per_min` | 30; nguyên, > 0; dành cho bonus chưa bật |

`WEATHER_RETRIES` và `WEATHER_CACHE_TTL_S` là phần Huy mở rộng từ starter để có thể cấu hình
và test chính sách weather. Factory truyền tất cả trường vào WeatherClient thật.
`X-API-Key` được đối chiếu với key trong Settings. Không cấu hình key thì mọi lần đọc feedback
đều nhận 401; giá trị `change-me` trong `.env.example` chỉ là placeholder demo.

## Timeout, retry và fallback đã kiểm tra

| Tình huống | HTTP / hành vi | Bằng chứng tự động |
|---|---|---|
| Upstream hợp lệ | 200, `stale=false` | `test_weather_sends_coordinates_timeout_and_caches` |
| Cache còn TTL | 200, không gọi upstream lần nữa | Cùng test trên; clock tiến 599 giây |
| Timeout hoặc connect error | Tối đa 2 attempts mặc định, rồi 503 nếu chưa cache | `test_upstream_failures_retry_once_then_api_503` |
| HTTP 429/500 từ upstream | Retry có giới hạn, 503 nếu chưa cache | Cùng test parametrized; không biến upstream 429 thành rate limit của API |
| JSON hỏng/thiếu field/sai cấu trúc | Validate trước khi cache; retry rồi 503 | Cùng test với text không phải JSON, list, current null/list, thiếu field |
| Attempt đầu timeout, lần sau thành công | 200, dữ liệu mới | `test_transient_timeout_recovers_on_retry` |
| Cache đúng ranh TTL, upstream lỗi | Refresh 2 attempts, 200 `stale=true` giữ dữ liệu cũ | `test_expired_cache_serves_stale_then_refresh_recovers` |
| Upstream phục hồi sau stale | 200 `stale=false`, cập nhật cache mới | Cùng test trên |
| `retries=0` | 1 attempt, không sleep | `test_zero_retries_means_one_attempt_no_sleep` |
| `cache_ttl_s=0` | Mỗi lần đọc đều refresh | `test_zero_cache_ttl_refreshes_each_call` |

Các test dùng `httpx.MockTransport` cùng clock/backoff giả, không gọi Internet và không đợi thật.
Fake handler ném ConnectTimeout/ReadTimeout giúp kiểm tra chính sách xử lý timeout; giá trị timeout
được kiểm tra trong request extensions, không tuyên bố đã đo deadline mạng thật.
HTTPX timeout áp dụng từng thao tác mạng trong mỗi attempt; đây không phải deadline tổng 3 giây.
Mặc định có 1 lần retry và backoff 0.2 giây giữa hai attempt; không sleep sau lần thất bại cuối.
Upstream lỗi chỉ log loại exception, không ghi URL, response body hay exception message chứa dữ liệu nhạy cảm.

Factory đóng HTTP client do nó tạo khi app shutdown. Nếu inject client, caller chịu trách nhiệm đóng.
Cache nằm trong RAM của từng WeatherClient; feedback trong RAM của từng app. Lab04 chưa có database.
Đây là kiểm tra chuyên trách T4/HW-H, không nhận bonus H3 vì chưa tích hợp một API công khai thứ hai.
