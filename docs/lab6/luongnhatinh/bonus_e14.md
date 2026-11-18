# Bonus H3 — Thử nghiệm cải thiện `E14` (`can I take 32 credits`) trên nhánh riêng

Nhánh thử nghiệm: `feat/lab06-bonus-e14-luongnhatinh` (tách từ `feat/lab06-personal-luongnhatinh` tại commit `1d5ac34`).

## 1. Nguyên nhân fail ở baseline

- Query `E14`: `"can I take 32 credits"` → sau khi bỏ stop words còn `["take", "32", "credits"]`.
- Chunk đúng `H26#6.1` (`6.1 Credit load`) dùng `"Credit"` (số ít) và `"registering"`, không có từ `"take"`, nên BM25 chỉ đạt **1.475** (< ngưỡng `2.0`).
- Chunk nhiễu `H26#7.2` (`7.2 Exam absence`) có cụm `"take the exam"` (IDF cao vì `"take"` chỉ xuất hiện ở 1/14 chunk), nên BM25 chấm **2.086** và trả sai quy định vắng thi.

## 2. Kết quả thử nghiệm trước và sau

1. **Thử cắt số nhiều `-s` thuần túy cho mọi token (không thay đổi đồng nghĩa):**
   - `H26#6.1` giảm xuống **1.425** (do `"credit"` xuất hiện thêm ở `F26#1`, làm giảm IDF) và `H26#7.2` vẫn giữ **2.086** → `E14` vẫn fail.
   - Đồng thời `E20` (`"tell me about exams"`) bị cắt `"exams"` → `"exam"`, khớp `H26#7.2` và làm tụt từ `16/20` (abstain `4/5`) xuống **15/20** (abstain `3/5`).

2. **Chuẩn hóa từ vựng có kiểm soát (`credits -> credit`, `take`/`register -> registering`):**
   - `E14` đưa `H26#6.1` lên đầu với điểm BM25 **2.679** (vượt ngưỡng `2.0`), trả lời đúng điều kiện phải có sự đồng ý của cố vấn học tập khi đăng ký quá 30 tín chỉ.
   - `E20` vẫn giữ nguyên `abstain`, không phát sinh hồi quy ở các ca còn lại.

| Bộ câu | Cấu hình | Đường | Đúng | Từ chối đúng | Fail IDs |
|---|---|---|---:|---:|---|
| 20 gốc | Baseline (`1d5ac34`) | retrieval / llm (stub) | 16/20 | 4/5 | E13 E14 E15 E19 |
| 20 gốc | Bonus E14 (`TOKEN_ALIASES`) | retrieval / llm (stub) | **17/20** | 4/5 | E13 E15 E19 |
| 25 cá nhân | Baseline (`1d5ac34`) | retrieval / llm (stub) | 20/25 | 5/7 | E13 E14 E15 E19 E40 |
| 25 cá nhân | Bonus E14 (`TOKEN_ALIASES`) | retrieval / llm (stub) | **21/25** | 5/7 | E13 E15 E19 E40 |
