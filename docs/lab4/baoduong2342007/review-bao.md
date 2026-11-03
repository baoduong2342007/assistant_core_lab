# Review hỗ trợ PR39 — 02/11/2026

Codex thực hiện theo yêu cầu của Dương; đây không phải xác nhận review độc lập do người học tự thực hiện.

- PR39 head: `e253d548f44e45c4eeab4b825eee5aba0286f825`.
- Đã đọc main, schemas, weather và test API. Bảo đã bật Part F và thêm test weather sai cấu trúc.
- Snapshot commit trên Windows/Python 3.13 với dependencies của repo: API + practice 24 passed. Đây là kiểm tra tập trung, không phải toàn bộ regression của PR39.
- Phát hiện: upstream trả `temperature_2m="NaN"` được Pydantic chuyển thành số không hữu hạn và cache; endpoint trả 500 khi serialize JSON. Cần chặn NaN/Infinity trước cache và giữ luồng 503 hoặc cache stale, thêm test vào file Lab04 mới. Chưa đủ điều kiện approve.
