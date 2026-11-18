# So sánh ba đường xử lý — Trương Quang Bảo Dương

Chạy ngày 18/11/2026, từ nhánh `feat/lab06-personal-baoduong2342007`, nền `80b9d3946ccc88d9a9eca21d9840432b3aee0db4`, với các thay đổi Lab 06 trong nhánh này; Python 3.12, provider stub offline, BM25, ngưỡng 2.0, KB 14 chunk. Thời gian tính bằng ms trên máy chạy và không đại diện cho môi trường khác; đúng nguồn không đảm bảo câu trả lời có đủ căn cứ.

| Bộ câu | Đường | Đúng | Từ chối đúng | p50 | max | ID sai |
|---|---|---:|---:|---:|---:|---|
| 20 gốc | deterministic | 7/20 | 5/5 | 0.0 | 1.0 | E01 E02 E05 E06 E07 E08 E09 E10 E11 E12 E13 E14 E15 |
| 20 gốc | retrieval | 16/20 | 4/5 | 0.0 | 0.2 | E13 E14 E15 E19 |
| 20 gốc | llm (stub) | 16/20 | 4/5 | 0.2 | 0.7 | E13 E14 E15 E19 |
| 25 cá nhân | deterministic | 9/25 | 7/7 | 0.0 | 0.7 | E01 E02 E05 E06 E07 E08 E09 E10 E11 E12 E13 E14 E15 E21 E22 E23 |
| 25 cá nhân | retrieval | 20/25 | 6/7 | 0.0 | 0.1 | E13 E14 E15 E19 E21 |
| 25 cá nhân | llm (stub) | 20/25 | 6/7 | 0.2 | 0.6 | E13 E14 E15 E19 E21 |

Tôi chọn retrieval có ngưỡng và trích nguồn cho handbook, có chuyển người phụ trách khi thiếu căn cứ.
Nó trả nguồn trực tiếp, chạy offline và trong bộ 20 câu có cùng số câu đạt với stub nhưng không cần gọi model.
Ưu tiên sửa E19 vì điểm tương đồng cao đưa đến câu trả lời không có căn cứ về thi mở tài liệu; E13 và E15 còn bị định tuyến sai, E14 lấy sai chunk.

H1: Với 5 câu E21–E25, E21 sai vì cụm “fee” bị router chuyển sang phép tính học phí thay vì thông tin thay thẻ; E22–E25 đạt theo tiêu chí script, còn E19 vẫn là trường hợp trả lời thiếu căn cứ.

Tái chạy từ root: `python eval/compare_paths.py --cases eval/cases_20.jsonl` và `python eval/compare_paths.py`; script gốc chấm từ chối theo path abstain hoặc intent unknown nên cần xem thêm hành vi thực tế.
