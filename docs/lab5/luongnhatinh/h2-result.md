# H2 Query & Analysis Results — Lương Nhật Minh (`luongnhatinh`)

## 1. Query H2

```sql
SELECT
    intent,
    COUNT(*) AS total_requests,
    SUM(CASE WHEN resolved = 0 THEN 1 ELSE 0 END) AS unresolved_count,
    ROUND(AVG(CASE WHEN resolved = 0 THEN 1.0 ELSE 0.0 END) * 100, 2) AS unresolved_rate_pct,
    SUM(CASE WHEN degraded = 1 THEN 1 ELSE 0 END) AS degraded_count,
    ROUND(AVG(latency_ms), 2) AS avg_latency_ms
FROM interaction
GROUP BY intent
ORDER BY total_requests DESC;
```

## 2. Kết quả chạy thực tế (từ `assistant-analysis.db` được seed 300 interactions)

| Intent | Total Requests | Unresolved Count | Unresolved Rate (%) | Degraded Count | Avg Latency (ms) |
|---|---:|---:|---:|---:|---:|
| `rule` | 140 | 0 | 0.00% | 34 | 76.18 |
| `fee` | 61 | 0 | 0.00% | 1 | 5.07 |
| `office` | 47 | 0 | 0.00% | 1 | 3.40 |
| `greeting` | 26 | 0 | 0.00% | 2 | 2.40 |
| `unknown` | 26 | 26 | 100.00% | 0 | 8.06 |

## 3. Diễn giải phân tích số liệu

1. **Phân bố truy vấn (Traffic Distribution):**
   - Ý định tra cứu quy chế (`rule`) chiếm tỷ trọng cao nhất với 140 / 300 lượt (46.7%), theo sau là tra cứu học phí (`fee` - 20.3%) và văn phòng (`office` - 15.7%).
   - Tỷ lệ `unknown` ở mức 8.7% (26 lượt), cho thấy phần lớn câu hỏi của sinh viên đã được bot nhận diện đúng ý định.

2. **Độ trễ xử lý (Latency Analysis):**
   - Ý định `rule` có thời gian phản hồi trung bình lớn nhất (76.18 ms) do cần tìm kiếm văn bản trong handbook JSON.
   - Các intent đơn giản (`greeting`, `office`, `fee`) phản hồi rất nhanh (2.4 ms – 5.07 ms).

3. **Chất lượng và độ tin cậy (Degraded & Failure Rate):**
   - 100% các request nhận diện là `unknown` đều không được giải quyết (`resolved = 0`), đúng với logic nghiệp vụ fallback.
   - Với intent `rule`, có 34 / 140 trường hợp (24.3%) bị degraded (chế độ suy giảm hiệu năng/kết quả phụ do fallback hoặc độ tự tin thấp), đây là khu vực trọng tâm cần tối ưu ở các tuần tiếp theo (như tích hợp RAG ở Lab06).
