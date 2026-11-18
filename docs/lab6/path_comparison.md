# So sánh ba đường xử lý — Trương Quang Bảo Dương

Chạy ngày 18/11/2026, từ nhánh `feat/lab06-personal-baoduong2342007`, nền `80b9d3946ccc88d9a9eca21d9840432b3aee0db4`, đo lại tại commit `21c4696`; Python 3.12, provider stub offline, BM25, ngưỡng 2.0, KB 14 chunk. Thời gian tính bằng ms trên máy chạy. Điểm nguồn đo ID trích dẫn, còn độ đầy đủ của câu trả lời cần kiểm tra riêng.

| Bộ câu | Đường | Đúng | Từ chối đúng | p50 | max | ID sai |
|---|---|---:|---:|---:|---:|---|
| 20 gốc | deterministic | 7/20 | 5/5 | 0.0 | 0.5 | E01 E02 E05 E06 E07 E08 E09 E10 E11 E12 E13 E14 E15 |
| 20 gốc | retrieval | 17/20 | 4/5 | 0.0 | 0.1 | E13 E14 E19 |
| 20 gốc | llm (stub) | 17/20 | 4/5 | 0.2 | 0.5 | E13 E14 E19 |
| 25 cá nhân | deterministic | 9/25 | 7/7 | 0.0 | 0.4 | E01 E02 E05 E06 E07 E08 E09 E10 E11 E12 E13 E14 E15 E21 E22 E23 |
| 25 cá nhân | retrieval | 22/25 | 6/7 | 0.0 | 0.1 | E13 E14 E19 |
| 25 cá nhân | llm (stub) | 22/25 | 6/7 | 0.2 | 0.5 | E13 E14 E19 |

Tôi chọn retrieval có ngưỡng và trích nguồn cho handbook, có chuyển người phụ trách khi thiếu căn cứ.
Nó trả nguồn trực tiếp, chạy offline và trong bộ 20 câu có cùng số câu đạt với stub nhưng không cần gọi model.
Ưu tiên sửa E19 vì điểm tương đồng cao đưa đến câu trả lời không có căn cứ về thi mở tài liệu.

Cả 5 câu H1 (E21–E25) đạt với retrieval và stub sau khi E21 được đưa qua KB và trích đủ mức phí thay thẻ, còn E19 vẫn trả lời dựa vào mục vắng thi dù mục đó không nói về thi mở tài liệu.

Bonus sửa E15 và E21. Tại commit `4db9d2c`, cả retrieval và stub đạt 16/20 và 20/25. Sau khi định tuyến câu hỏi về mượn sách và phí thay thẻ qua KB, kết quả tăng thành 17/20 và 22/25. Hai test API kiểm cả nguồn lẫn nội dung trả về. Các lỗi còn lại gồm E13 (hạn đóng học phí đi qua calculator), E14 (xếp sai chunk) và E19 (nguồn không trả lời câu hỏi).

Chạy từ root với `python eval/compare_paths.py --cases eval/cases_20.jsonl` và `python eval/compare_paths.py`. Script chấm từ chối theo path abstain hoặc intent unknown.
