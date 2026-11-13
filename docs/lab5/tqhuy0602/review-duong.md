# Review cục bộ PR #44 — API persistence của Dương

Kiểm tra commit `3f51c7bb2bfb9b0de60e3c3380e6b65a9406cff9` trên nhánh API. Ghi chú dưới đây là bản review cục bộ. [PR #44](https://github.com/baoduong2342007/assistant_core_lab/pull/44)

## `created_at` mất thông tin múi giờ trong phản hồi HTTP

`POST /v1/feedback` trước đây tạo thời điểm bằng `datetime.now(timezone.utc)` và trả chuỗi có hậu tố `Z`. Sau khi đọc lại từ SQLite, cả `POST /v1/feedback` và `GET /v1/feedback` trả chuỗi như `2026-11-13T06:33:39.388096`, thiếu offset. Client phân tích thời điểm theo giờ địa phương có thể hiển thị sai giờ. Trong `src/assistant_api/main.py`, chuẩn hóa `created_at` đọc từ SQLite về UTC tại ranh giới API và thêm test cho hai endpoint, gồm đọc lại sau restart.

Tái hiện trên bản tích hợp bằng chat → tạo feedback → liệt kê feedback với admin key. Cả hai response trả cùng timestamp thiếu offset. Luồng lưu `request_id`, mã phiên và phản hồi 404 cho request ID lạ đã được kiểm tra qua suite tích hợp.
