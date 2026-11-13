# Lab05 — kết quả F1–F3 của Phan Quỳnh Quyền

Chạy ngày 13/11/2026 (Asia/Bangkok), trên SQLite tạm, dữ liệu hoàn toàn giả lập.
Nguồn: [public_materials tại commit d795a1a](https://github.com/CSC10014-at-fit-hcmus/public_materials/tree/d795a1a09f430d83b0c69b45da1689984a1254b5/lab05).
Migration 001/002 của học liệu chạy trên DB sạch rồi chạy lại để kiểm tra skip.
Seed nguyên bản dùng `random.seed(7)`, 300 interactions; R1/R2 được hoàn thiện bằng
[bản cá nhân](feedback_repository.py). Đã chạy với models starter và `db.py` của Bảo
tại `1f49c5458cae166bcf9076837aa72d71bac5cdeb`: kết quả tổng hợp giống nhau.

DB có **59 chat_session, 300 interaction, 96 feedback**. UUID và thời gian thay đổi
theo lần chạy; seed cố định tạo cùng phân bố thống kê trên môi trường đã kiểm tra.
[SQL tích hợp](../../../sql/my_queries.sql) và [JSON thực chạy](query-results.json)
giữ tên cột, số hàng và giá trị trả về.

## F1 — số request theo intent

Shape: 5 hàng × 2 cột. Đơn vị: interaction. Thứ tự: số request giảm dần, intent tăng dần khi bằng nhau.

| intent | request_count |
| --- | ---: |
| rule | 140 |
| fee | 61 |
| office | 47 |
| greeting | 26 |
| unknown | 26 |

Tổng 300 khớp số interaction đã seed. Rule chiếm 46,67% trong bộ dữ liệu này;
đây là phân bố giả lập, chưa phản ánh nhu cầu người dùng thực.

## F2 — latency trung bình theo intent

Shape: 5 hàng × 2 cột. Đơn vị: millisecond (ms), làm tròn 2 chữ số thập phân.
Thứ tự: latency giảm dần, intent tăng dần khi bằng nhau.

| intent | avg_latency_ms |
| --- | ---: |
| rule | 76.18 |
| unknown | 8.06 |
| fee | 5.07 |
| office | 3.40 |
| greeting | 2.40 |

Mỗi interaction đóng góp một lần; không JOIN feedback vì một request có thể nhận
nhiều rating. Rule chậm nhất trong mẫu; seed chủ động gán base latency lớn hơn cho
rule và nhân latency khi degraded. Chưa thể kết luận đây là lỗi hiệu năng API.

## F3 — topic nhận thumbs-down nhiều nhất

Shape: 3 hàng × 2 cột. Đơn vị: sự kiện feedback có `rating = -1`.
Thứ tự: số thumbs-down giảm dần, topic tăng dần khi bằng nhau.

| topic | thumbs_down_count |
| --- | ---: |
| H26-4.2 | 8 |
| H26-5.3 | 8 |
| H26-7.2 | 2 |

JOIN qua `feedback.request_id = interaction.request_id`; topic NULL bị loại.
Hai thumbs-down cho một request được đếm thành hai sự kiện. 18 là số rating âm
có topic trong mẫu, không phải tổng rating âm toàn DB. Đây không phải tỷ lệ hài
lòng: topic nhiều request có thể nhận nhiều rating âm hơn.

[H2 và diễn giải](h2-result.md) bổ sung unresolved, degraded và latency theo intent.
