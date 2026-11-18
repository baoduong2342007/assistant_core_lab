# So sánh ba đường xử lý — Trương Quang Bảo Dương

Chạy ngày 18/11/2026, từ nhánh `feat/lab06-personal-baoduong2342007`, nền `80b9d3946ccc88d9a9eca21d9840432b3aee0db4`, đo lại tại commit `e215cf4`; Python 3.12, provider stub offline, BM25, ngưỡng 2.0, KB 14 chunk. Thời gian tính bằng ms trên máy chạy. Điểm nguồn đo ID trích dẫn, còn độ đầy đủ của câu trả lời cần kiểm tra riêng.

| Bộ câu | Đường | Đúng | Từ chối đúng | p50 | max | ID sai |
|---|---|---:|---:|---:|---:|---|
| 20 gốc | deterministic | 7/20 | 5/5 | 0.0 | 1.1 | E01 E02 E05 E06 E07 E08 E09 E10 E11 E12 E13 E14 E15 |
| 20 gốc | retrieval | 20/20 | 5/5 | 0.0 | 0.1 | — |
| 20 gốc | llm (stub) | 20/20 | 5/5 | 0.2 | 0.8 | — |
| 25 cá nhân | deterministic | 9/25 | 7/7 | 0.0 | 0.6 | E01 E02 E05 E06 E07 E08 E09 E10 E11 E12 E13 E14 E15 E21 E22 E23 |
| 25 cá nhân | retrieval | 25/25 | 7/7 | 0.0 | 0.1 | — |
| 25 cá nhân | llm (stub) | 25/25 | 7/7 | 0.2 | 0.6 | — |

Tôi chọn retrieval có ngưỡng và trích nguồn cho handbook, có chuyển người phụ trách khi thiếu căn cứ.
Nó chạy offline và đạt cùng kết quả với stub trên cả hai bộ câu.
Sau khi sửa E19, tôi ưu tiên kiểm tra thêm câu hỏi về các quy định vắng mặt trong KB vì BM25 vẫn có thể xếp cao đoạn chỉ trùng từ khóa.

Cả 5 câu H1 (E21–E25) đạt với retrieval và stub, gồm E21 trả đúng phí thay thẻ từ S26#3 và E24–E25 trả path abstain.

Bản đầu đạt 16/20 và 20/25 với retrieval và stub. Sửa định tuyến câu mượn sách và phí thay thẻ đưa kết quả lên 17/20 và 22/25. Bản cuối bổ sung từ khóa theo cách gọi trong KB cho hạn đóng học phí (E13) và tải tín chỉ (E14), đồng thời yêu cầu nguồn phải có nội dung về thi mở hoặc đóng tài liệu (E19). Bản cuối đạt 20/20 và 25/25. Bộ câu và đáp án kỳ vọng giữ nguyên qua các lần đo.

Chạy từ root với `python eval/compare_paths.py --cases eval/cases_20.jsonl` và `python eval/compare_paths.py`. Bản cuối chỉ tính từ chối đúng khi path là abstain.
