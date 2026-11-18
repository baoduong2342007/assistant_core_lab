# So sánh ba đường xử lý Lab 06 của nhóm

Các kết quả dưới đây chạy trên bản tích hợp với Python 3.12, provider stub offline, BM25 ngưỡng 2.0 và 14 chunk. Bộ 40 câu gồm 20 câu gốc và 5 câu từ mỗi PR cá nhân đã có của Dương, Quyền, Minh và Bảo. Dải E26–E30 dành cho Huy và có thể bổ sung khi PR cá nhân của Huy sẵn sàng.

| Bộ câu | Đường | Đúng | Từ chối đúng | p50 (ms) | max (ms) | ID sai |
|---|---|---:|---:|---:|---:|---|
| 20 gốc | deterministic | 7/20 | 5/5 | 0.0 | 0.3 | E01 E02 E05 E06 E07 E08 E09 E10 E11 E12 E13 E14 E15 |
| 20 gốc | retrieval | 20/20 | 5/5 | 0.0 | 0.1 | — |
| 20 gốc | llm (stub) | 20/20 | 5/5 | 0.1 | 0.5 | — |
| 40 nhóm | deterministic | 15/40 | 13/13 | 0.0 | 0.3 | E01 E02 E05 E06 E07 E08 E09 E10 E11 E12 E13 E14 E15 E21 E22 E23 E31 E32 E33 E36 E37 E38 E41 E42 E43 |
| 40 nhóm | retrieval | 40/40 | 13/13 | 0.0 | 0.1 | — |
| 40 nhóm | llm (stub) | 40/40 | 13/13 | 0.1 | 0.5 | — |

Nhóm chọn retrieval có ngưỡng cho câu hỏi quy định và giữ phép tính học phí ở đường deterministic.
Retrieval đạt cùng số câu đúng với stub trong lần chạy này và trả trực tiếp đoạn nguồn.
Bộ câu nhóm phát hiện ba trường hợp trùng chủ đề nhưng thiếu căn cứ, nên hệ thống kiểm chủ đề thiết bị trước khi dùng các đoạn về thi hoặc mượn sách để trả lời.

E35 và E40 hỏi thiết bị được phép dùng khi thi. E45 hỏi mượn laptop. Trước khi sửa, retrieval và stub đạt 37/40 vì cả ba câu nhận đoạn liên quan gián tiếp. Sau khi yêu cầu đoạn nguồn đề cập thiết bị, cả ba đều trả abstain. Kết quả 40/40 áp dụng cho bộ câu mẫu và các tiêu chí của script.

Đo lại với `python eval/compare_paths.py --cases eval/cases_20.jsonl` và `python eval/compare_paths.py`. Bảng cá nhân và báo cáo bonus nằm trong thư mục tương ứng dưới `docs/lab6/`.

Các PR đưa vào bản tích hợp gồm [#49](https://github.com/baoduong2342007/assistant_core_lab/pull/49), [#50](https://github.com/baoduong2342007/assistant_core_lab/pull/50), [#51](https://github.com/baoduong2342007/assistant_core_lab/pull/51) và [#53](https://github.com/baoduong2342007/assistant_core_lab/pull/53). [PR bonus #52](https://github.com/baoduong2342007/assistant_core_lab/pull/52) đóng góp báo cáo thử nghiệm. Bản nhóm giữ mở rộng truy vấn tải tín chỉ cho E14 để tránh thay nghĩa mọi lần xuất hiện của take hoặc register.
