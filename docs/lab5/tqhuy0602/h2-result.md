# H2 — Tỷ lệ phản hồi dùng phương án dự phòng theo chủ đề

Nguồn là 300 interaction và 96 feedback **giả lập**. Chạy migration `001` và `002` trên SQLite mới, sau đó chạy script `seed.py` của học liệu với SQLModel 0.0.22 và repository từ nhánh tích hợp API `3f51c7b`. Script cố định seed ngẫu nhiên ở `7`.

| Mã chủ đề | Số lượt hỏi | Lượt dùng phương án dự phòng | Tỷ lệ (%) | Trung bình thông thường (ms) | Trung bình dự phòng (ms) |
| --- | ---: | ---: | ---: | ---: | ---: |
| H26-7.2 | 11 | 4 | 36.36 | 64.69 | 236.30 |
| H26-4.2 | 45 | 11 | 24.44 | 46.29 | 184.20 |
| H26-5.3 | 84 | 19 | 22.62 | 39.43 | 163.38 |

[Truy vấn H2](h2.sql) trả 3 dòng, gồm 140 lượt hỏi có `intent = 'rule'` và có mã chủ đề. Mẫu H26-7.2 đứng đầu về tỷ lệ (4/11), còn H26-5.3 có nhiều lượt dùng phương án dự phòng nhất (19). Script seed đặt phân bố cho chủ đề, cờ `degraded` và độ trễ. Các số liệu mô tả dữ liệu giả lập.

Chạy lại từ thư mục gốc của repo này. Trỏ `LAB05_STARTER` đến `lab05/starter` của học liệu tại `d795a1a` và `LAB05_API_CHECKOUT` đến bản tích hợp có R1/R2 hoạt động.

```sh
analysis_dir=$(mktemp -d)
python "$LAB05_STARTER/scripts/migrate.py" "$analysis_dir/assistant-analysis.db"
PYTHONPATH="$LAB05_API_CHECKOUT/src" python "$LAB05_STARTER/scripts/seed.py" "$analysis_dir/assistant-analysis.db" 300
sqlite3 -header -column "$analysis_dir/assistant-analysis.db" < docs/lab5/tqhuy0602/h2.sql
```
