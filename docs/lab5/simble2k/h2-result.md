# Báo cáo Phân tích Truy vấn H2 — Phạm Quốc Bảo (`simble2k`)

- **Ngày thực hiện:** 10/11/2026
- **Cơ sở dữ liệu:** `assistant-analysis.db` (áp dụng migration 001/002, seed 300 tương tác giả lập)
- **Tập tin truy vấn:** `docs/lab5/simble2k/h2.sql`

---

## 1. Mục tiêu phân tích

Đánh giá độ tin cậy (reliability) và hiệu năng (latency) của trợ lý học tập theo từng loại ý định (`intent`):
- `total_requests`: Tổng số lượt yêu cầu được ghi nhận.
- `unresolved_count` & `unresolved_rate_pct`: Số lượng và tỷ lệ các yêu cầu không thể giải quyết (`resolved = 0`).
- `degraded_count`: Số lượng yêu cầu bị giảm chất lượng hoặc xử lý chậm (`degraded = 1`).
- `avg_latency_ms`: Thời gian xử lý trung bình tính bằng mili-giây.

---

## 2. Kết quả truy vấn thực tế

| Intent | Total Requests | Unresolved Count | Unresolved Rate (%) | Degraded Count | Avg Latency (ms) |
|---|:---:|:---:|:---:|:---:|:---:|
| **`rule`** | 140 | 0 | 0.00% | 34 | 76.18 |
| **`fee`** | 61 | 0 | 0.00% | 1 | 5.07 |
| **`office`** | 47 | 0 | 0.00% | 1 | 3.40 |
| **`greeting`** | 26 | 0 | 0.00% | 2 | 2.40 |
| **`unknown`** | 26 | 26 | 100.00% | 0 | 8.06 |

---

## 3. Diễn giải và Nhận xét kỹ thuật

1. **Phân bố lưu lượng (Traffic Distribution):**
   - Ý định `rule` (tra cứu quy chế/sổ tay sinh viên) chiếm phần lớn lưu lượng (140/300 requests, tương đương 46.7%), phản ánh nhu cầu hỏi về học vụ của sinh viên là cao nhất.
   - Các ý định tra cứu học phí (`fee`) và phòng ban (`office`) chiếm lần lượt 20.3% và 15.7%.
2. **Độ tin cậy (Reliability):**
   - Tất cả các intent có chủ đích (`rule`, `fee`, `office`, `greeting`) đều đạt tỷ lệ giải quyết thành công tuyệt đối (**100% resolved**, 0% unresolved).
   - Nhóm `unknown` có 100% unresolved, phản ánh các câu hỏi nằm ngoài phạm vi tri thức hoặc không phân loại được intent, hệ thống ghi nhận đúng bản chất kỹ thuật.
3. **Hiệu năng & Trạng thái suy giảm (Latency & Degradation):**
   - `greeting`, `office`, `fee` có độ trễ cực thấp (2.4ms đến 5.07ms) do dữ liệu tra cứu nhẹ và dùng bộ nhớ trực tiếp.
   - `rule` có độ trễ cao nhất (76.18ms) và có 34 lượt bị degraded (24.3%), do việc tìm kiếm và lọc danh mục quy định cần đối sánh nhiều tiêu chí phức tạp hơn.
