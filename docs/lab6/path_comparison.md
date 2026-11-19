# Lab 06 — So sánh ba chế độ (`luongnhatinh`)

Thực hiện bởi **Lương Nhật Minh (`luongnhatinh`)** trên nhánh `feat/lab06-personal-luongnhatinh` (nền `80b9d39`, đo tại commit `46cea8bbb2043b01ca74eafadab5cc3394137823`), Windows Python 3.11, provider `stub` offline, index `bm25`, ngưỡng `min_score = 2.0`, `k = 3`, KB 14 chunk.

Lệnh chạy từ root repo:

```powershell
$env:LLM_PROVIDER = 'stub'
python eval/compare_paths.py --cases eval/cases_20.jsonl
python eval/compare_paths.py
```

## 1. Bảng 20 câu gốc (`E01–E20`)

| Path | Correct | Abstain ok | p50 (ms) | Max (ms) | Controllability (1–5) | Main failure mode | Fail IDs |
|---|---:|---:|---:|---:|---:|---|---|
| deterministic | 7/20 | 5/5 | 0.0 | 0.6 | 5 | Không trả lời được các câu hỏi quy định (`EMPTY` index) | E01 E02 E05 E06 E07 E08 E09 E10 E11 E12 E13 E14 E15 |
| retrieval | 16/20 | 4/5 | 0.0 | 0.1 | 4 | Lỗi router (`E13`, `E15`), lệch từ khóa BM25 (`E14`) và khớp nhầm từ chung (`E19`) | E13 E14 E15 E19 |
| llm (stub) | 16/20 | 4/5 | 0.2 | 0.5 | 4 | Kế thừa nguyên tập lỗi router/retrieval ở tầng đầu vào (`E13`, `E14`, `E15`, `E19`) | E13 E14 E15 E19 |

Tôi chọn chế độ `retrieval` có ngưỡng `min_score = 2.0` và trích dẫn nguồn làm đường mặc định an toàn cho câu hỏi handbook. Nó đạt cùng độ chính xác `16/20` như `llm (stub)`, trích nguyên văn quy định chính thức không bịa chi tiết và giữ độ trễ `p50 = 0.0 ms` hoàn toàn offline. Tôi ưu tiên sửa `E19` trước vì câu hỏi ngoài tài liệu (`is the final exam open-book`) vẫn vượt ngưỡng BM25 (`5.620`) do trùng cụm `"final exam"` với đoạn vắng thi `H26#7.2`.

## 2. Bảng 25 câu gồm H1 (`E01–E20` và `E36–E40`)

| Path | Correct | Abstain ok | p50 (ms) | Max (ms) | Controllability (1–5) | Main failure mode | Fail IDs |
|---|---:|---:|---:|---:|---:|---|---|
| deterministic | 9/25 | 7/7 | 0.0 | 0.6 | 5 | Thiếu tra cứu tài liệu nên trượt toàn bộ câu quy định mới (`E36–E38`) | E01 E02 E05 E06 E07 E08 E09 E10 E11 E12 E13 E14 E15 E36 E37 E38 |
| retrieval | 20/25 | 5/7 | 0.0 | 0.1 | 4 | Vẫn trượt 4 ca gốc và trượt thêm `E40` do khớp giả từ khóa `"final exam"` | E13 E14 E15 E19 E40 |
| llm (stub) | 20/25 | 5/7 | 0.2 | 0.5 | 4 | Phụ thuộc chất lượng router và top hit BM25 nên trượt cùng 5 ca `E13 E14 E15 E19 E40` | E13 E14 E15 E19 E40 |

Trong 5 câu H1 (`E36–E40`), `E36` (`F26#1`), `E37` (`H26#5.4`), `E38` (`S26#2`) đều trích đúng nguồn và `E39` bị chặn bởi privacy guard trước khi retrieval, còn `E40` (`are smartwatches allowed during the final exam`) fail tương tự `E19` vì BM25 chấm `H26#7.2` đạt `5.620` dù đoạn đó chỉ nói về vắng thi y tế.

## 3. Rà soát các case trọng tâm (`E03`, `E04`, `E13`, `E14`, `E15`, `E19`)

- `E03` (`tuition for 18 credits and 2 retake`): trả `Your tuition is 9,450,000 VND.` qua deterministic calculator (`intent=fee`).
- `E04` (`where is the library`): trả `Library: room B.201, open Mon-Sat 07:00-20:00.` qua deterministic directory (`intent=office`).
- `E13` (`when is tuition due`): router bắt từ khóa `"tuition"` đưa vào nhánh `fee` (`How many credits?`), đồng thời BM25 riêng cũng xếp `F26#1` (`2.277`) trên `F26#3` (`1.484`).
- `E14` (`can I take 32 credits`): BM25 xếp `H26#7.2` (`2.086`, khớp từ `"take"`) cao hơn `H26#6.1` (`1.475`, dùng `"registering"` và `"credit"` số ít).
- `E15` (`how long can I keep a library book`): router bắt tên phòng `"library"` trả vị trí `B.201` thay vì chuyển sang RAG lấy `S26#1` (`2.299`).
- `E19` (`is the final exam open-book`): BM25 khớp `H26#7.2` với điểm `5.620 >= 2.0`, minh họa điểm retrieval cao chưa bảo đảm đúng ngữ nghĩa.
