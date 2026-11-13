# H2 Query & Analysis Results — Lương Nhật Minh (`luongnhatinh`)

## 1. Mục đích và Query H2

Query H2 thực hiện trích xuất và tổng hợp các chỉ số độ tin cậy, tỷ lệ phản hồi suy giảm và phân phối độ trễ trên bảng `interaction`.

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

---

## 2. Kết quả truy vấn thực tế

*Môi trường thực thi:* Chạy trên cơ sở dữ liệu phân tích `assistant-analysis.db` sau khi áp dụng migration và nạp 300 bản ghi giả lập từ `scripts/seed.py` (`random.seed(7)`, `n = 300`).

| Intent | Total Requests | Unresolved Count | Unresolved Rate (%) | Degraded Count | Avg Latency (ms) |
|---|---:|---:|---:|---:|---:|
| `rule` | 140 | 0 | 0.00% | 34 | 76.18 |
| `fee` | 61 | 0 | 0.00% | 1 | 5.07 |
| `office` | 47 | 0 | 0.00% | 1 | 3.40 |
| `greeting` | 26 | 0 | 0.00% | 2 | 2.40 |
| `unknown` | 26 | 26 | 100.00% | 0 | 8.06 |

---

## 3. Diễn giải và Kiểm chứng Kỹ thuật

> [!NOTE]
> **Bản chất dữ liệu:** Toàn bộ 300 tương tác trong bảng `interaction` là **dữ liệu tổng hợp giả lập (synthetic simulation data)** được sinh tự động bởi `scripts/seed.py` nhằm phục vụ việc kiểm thử hiệu năng truy vấn, tính đúng đắn của schema và các phép tổng hợp SQL. Dữ liệu này **không** phản ánh lưu lượng truy cập thực tế của sinh viên, độ chính xác của mô hình phân loại intent hay thời gian thực thi I/O thực tế khi tra cứu handbook JSON.

### Đối chiếu tính chính xác của câu truy vấn SQL với cấu hình phân phối của generator:

1. **Phân bố số lượng yêu cầu (`total_requests`):**
   - Script `seed.py` định nghĩa phân phối xác suất ngẫu nhiên thông qua `WEIGHTS = [10, 20, 15, 25, 15, 5, 10]` tương ứng với các intent: `greeting` (10%), `fee` (20%), `office` (15%), 3 biến thể của `rule` ($25 + 15 + 5 = 45\%$) và `unknown` (10%).
   - Kết quả nhóm `GROUP BY intent` từ SQL ghi nhận:
     - `rule`: 140 / 300 = **46.67%** (kỳ vọng: 45%)
     - `fee`: 61 / 300 = **20.33%** (kỳ vọng: 20%)
     - `office`: 47 / 300 = **15.67%** (kỳ vọng: 15%)
     - `greeting`: 26 / 300 = **8.67%** (kỳ vọng: 10%)
     - `unknown`: 26 / 300 = **8.67%** (kỳ vọng: 10%)
   - $\rightarrow$ Câu lệnh `COUNT(*)` và `GROUP BY intent` phản ánh chính xác phân phối mẫu từ generator theo luật số lớn.

2. **Tỷ lệ chưa giải quyết (`unresolved_rate_pct`):**
   - Theo định nghĩa mô phỏng: `resolved = (intent != "unknown")`.
   - Kết quả truy vấn thể hiện tính nhất quán tuyệt đối:
     - Với `intent = 'unknown'`, toàn bộ 26/26 bản ghi có `resolved = 0`, tỷ lệ chưa giải quyết là **100.00%**.
     - Với các intent còn lại, không có bản ghi nào chưa giải quyết (`unresolved_count = 0`, `unresolved_rate_pct = 0.00%`).
   - $\rightarrow$ Mệnh đề `SUM(CASE WHEN resolved = 0 THEN 1 ELSE 0 END)` tính toán chính xác số lượng và tỷ lệ phần trăm thất bại.

3. **Phân phối độ trễ trung bình (`avg_latency_ms`):**
   - Trong `seed.py`, độ trễ được sinh bằng `random.gauss(base_ms * (4 if degraded else 1), base_ms / 3)`:
     - Intent `greeting`, `office`, `fee` có `base_ms` lần lượt là 2, 3, 5 ms; độ trễ trung bình truy vấn tương ứng là 2.40 ms, 3.40 ms, 5.07 ms.
     - Intent `unknown` có `base_ms = 8`, giá trị trung bình truy vấn là 8.06 ms.
     - Intent `rule` có `base_ms` dao động từ 40 đến 60 ms và có 34 trường hợp bị `degraded` (kích hoạt hệ số nhân $\times 4$), đưa độ trễ trung bình lên 76.18 ms.
   - $\rightarrow$ Phép tính `ROUND(AVG(latency_ms), 2)` tính toán chính xác độ trễ trung bình cho từng nhóm ý định.
