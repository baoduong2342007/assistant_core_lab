# H2 — intent nào có tỷ lệ chưa giải quyết cao nhất?

Chạy [h2.sql](h2.sql) ngày 13/11/2026 trên DB giả lập trong [báo cáo F1–F3](query-results.md).
SQL cũng là phần H2 của `sql/my_queries.sql`; test kiểm tra hai bản luôn khớp nhau.
Shape: **5 hàng × 6 cột**. Một hàng cho mỗi intent có interaction.

| intent | request_count | unresolved_count | unresolved_rate_pct | degraded_count | avg_latency_ms |
| --- | ---: | ---: | ---: | ---: | ---: |
| unknown | 26 | 26 | 100.00 | 0 | 8.06 |
| rule | 140 | 0 | 0.00 | 34 | 76.18 |
| fee | 61 | 0 | 0.00 | 1 | 5.07 |
| office | 47 | 0 | 0.00 | 1 | 3.40 |
| greeting | 26 | 0 | 0.00 | 2 | 2.40 |

`unresolved_count` đếm `resolved = 0`. Mẫu số là **tất cả interaction của intent**,
kể cả request không nhận feedback. `100.0` tránh chia số nguyên. `degraded_count`
đếm `degraded = 1` độc lập với resolved. Latency tính bằng ms. Thứ tự: tỷ lệ
unresolved giảm dần, số request giảm dần, intent tăng dần. DB rỗng trả 0 hàng.

Có 26/300 request unresolved (8,67%), tất cả thuộc unknown; 38/300 degraded (12,67%).
Generator đặt `resolved = intent != 'unknown'`. Kết quả 100% của unknown và 0% của
các intent khác do quy tắc này, không chứng minh chất lượng thật. Rule có 34/140
degraded (24,29%) và latency trung bình cao nhất; đây là tình huống giả lập để luyện
phát hiện nhóm cần xem xét. Cần metadata thực, khoảng thời gian và cỡ mẫu phù hợp
trước khi quyết định cải thiện sản phẩm.

Không JOIN feedback nên nhiều rating/request không thay đổi mẫu số. Test dùng mẫu
riêng có request vừa resolved vừa degraded, request không có feedback, nhiều rating
và DB rỗng để kiểm tra các trường hợp này.
