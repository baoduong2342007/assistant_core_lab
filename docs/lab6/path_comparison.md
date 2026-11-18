# Lab 06 — So sánh ba chế độ

Kết quả của **Phan Quỳnh Quyền (pqquyenn)** để Quyền và Minh đối chiếu khi chạy lại trên bản tích hợp. Mã được đo tại commit **5ef690e1befa80c643b5a754eec209518b6fd686**, trên Windows với Python 3.11.9, provider **stub** và bộ tài liệu mẫu gồm 14 chunk. Hai chế độ dùng tài liệu chạy **BM25** với ngưỡng **2.0** và **k = 3**. Chế độ deterministic dùng index rỗng để đánh giá riêng router, công cụ và hành vi từ chối.

Từ root repo, chạy các lệnh sau trong môi trường đã cài `python -m pip install -r requirements.txt` và `python -m pip install -e .`.

```text
python eval/compare_paths.py --baseline
python eval/compare_paths.py
```

Latency tính theo mili giây cho mỗi lần gọi `AssistantService.handle`, sau khi tải KB và dựng index. Cột từ chối đúng dùng cách chấm của học liệu, chấp nhận `path=abstain` hoặc `intent=unknown`. Các test A1 kiểm trực tiếp đường đi, escalation, confidence và số lượt gọi provider.

## 20 câu gốc (E01–E20)

| Chế độ | Đúng | Từ chối đúng | p50 (ms) | Max (ms) | Case fail |
| --- | ---: | ---: | ---: | ---: | --- |
| Deterministic | 7/20 | 5/5 | 0.006 | 0.299 | E01 E02 E05 E06 E07 E08 E09 E10 E11 E12 E13 E14 E15 |
| Retrieval | 16/20 | 4/5 | 0.017 | 0.046 | E13 E14 E15 E19 |
| LLM (stub) | 16/20 | 4/5 | 0.082 | 0.935 | E13 E14 E15 E19 |

Mình chọn retrieval cho câu hỏi handbook. Retrieval đạt cùng 16/20 với stub trong lần đo này, trích trực tiếp đoạn nguồn và có p50 thấp hơn. Mình ưu tiên sửa E19 vì câu hỏi về thi mở tài liệu nhận đoạn quy định vắng thi dù BM25 chấm đoạn đó 5.620.

## 25 câu gồm H1 (E01–E20 và E31–E35)

| Chế độ | Đúng | Từ chối đúng | p50 (ms) | Max (ms) | Case fail |
| --- | ---: | ---: | ---: | ---: | --- |
| Deterministic | 9/25 | 7/7 | 0.006 | 0.289 | E01 E02 E05 E06 E07 E08 E09 E10 E11 E12 E13 E14 E15 E31 E32 E33 |
| Retrieval | 20/25 | 5/7 | 0.017 | 0.045 | E13 E14 E15 E19 E35 |
| LLM (stub) | 20/25 | 5/7 | 0.079 | 0.474 | E13 E14 E15 E19 E35 |

Trong năm câu H1, retrieval và stub đều tìm đúng nguồn cho E31–E33, từ chối E34 vì không có hit và trả nhầm đoạn vắng thi `H26#7.2` cho E35 vì đoạn này chứa cụm “final exam” nhưng không có quy định dùng máy tính.

## Kiểm tra nguồn và lỗi định tuyến

| Case | Top hit BM25 | Quan sát |
| --- | --- | --- |
| E01 · Đăng ký luận văn với 118 tín chỉ | `H26#5.3` · 4.914 | Nguồn nêu tối thiểu 120 tín chỉ tích lũy và GPA 2.0. |
| E05 · Mất thẻ sinh viên | `S26#3` · 9.836 | Nguồn chỉ đến phòng I.102. |
| E13 · Hạn đóng học phí | `F26#1` · 2.277 | Router đưa vào tính phí. Nguồn hạn đóng `F26#3` đứng thứ hai với 1.484. |
| E14 · Đăng ký 32 tín chỉ | `H26#7.2` · 2.086 | Nguồn đúng `H26#6.1` chỉ đạt 1.475. Từ “take” khớp với câu nói về thi lại trong đoạn vắng thi. |
| E15 · Thời gian mượn sách | `S26#1` · 2.299 | Router trả vị trí thư viện thay vì chuyển sang retrieval. |
| E16 · Thủ đô nước Pháp | Không có hit | A1 từ chối trước khi gọi provider. |
| E19 · Thi mở tài liệu | `H26#7.2` · 5.620 | ID có trong KB, nhưng đoạn chỉ nói về vắng thi do lý do y tế. |
| E31 · Công nhận tín chỉ | `H26#8.3` · 16.680 | Cần nội dung tương đồng ít nhất 80% và điểm ít nhất 5.0/10. |
| E32 · Nơi làm lại thẻ | `S26#3` · 12.089 | Quy định ghi Student Affairs, phòng I.102. |
| E33 · Hoàn học phí khi rút môn | `F26#4` · 16.509 | Hoàn toàn bộ học phí của môn nếu rút trước khi hết tuần 2. |

E03 trả **9,450,000 VND** và E04 trả **B.201** ở cả ba chế độ. Khi CLI/API của nhóm dùng chung factory RAG, Minh và Quyền có thể chạy lại hai lệnh trên cùng commit tích hợp để cập nhật bảng nhóm.

Các tài liệu, bài mini search và 20 câu gốc lấy từ học liệu tại commit 11d934c. [Lab 06 của môn](https://github.com/CSC10014-at-fit-hcmus/public_materials/tree/11d934ccf8de9b0cf057d69afd84f2e2cf343dc9/lab06)
