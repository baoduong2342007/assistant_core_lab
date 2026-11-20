# Lab 06 — Trần Quốc Huy (`tqhuy0602`)

Đo ngày 20/11/2026, Asia/Ho_Chi_Minh; Python 3.11.16, macOS arm64.
Code commit: `e970ec1d2c09eb04417557c2ac0e9baa11074349`; nhánh cá nhân dựa trên main `28729b8` đã tích hợp bài của bốn thành viên.
Provider **stub offline**, index **BM25**, min_score **2.0**, **14 chunk**, k=3, retry=1, prompt `answer_v1`.
Đây là kết quả trên bản tích hợp hiện tại; các sửa router/retrieval E13–E15/E19 đã có từ main, không được nhận là đóng góp mới của Huy.

| Bộ câu | Đường | Đúng | Từ chối đúng | p50 (ms) | max (ms) | Khả năng kiểm soát (1–5, nhận định) | Lỗi chính | ID sai |
|---|---|---:|---:|---:|---:|---:|---|---|
| 20 gốc | deterministic | 7/20 | 5/5 | 0.0 | 0.2 | 5 | Không trả lời quy định từ KB | E01 E02 E05 E06 E07 E08 E09 E10 E11 E12 E13 E14 E15 |
| 20 gốc | retrieval | 20/20 | 5/5 | 0.0 | 0.0 | 4 | Có thể chọn đoạn cùng từ khóa nhưng thiếu căn cứ | — |
| 20 gốc | llm (stub) | 20/20 | 5/5 | 0.1 | 0.6 | 3 | Stub trích nguồn đầu tiên; không xác minh ý nghĩa | — |
| 25 cá nhân | deterministic | 9/25 | 7/7 | 0.0 | 0.2 | 5 | Không trả lời quy định từ KB | E01 E02 E05 E06 E07 E08 E09 E10 E11 E12 E13 E14 E15 E26 E27 E28 |
| 25 cá nhân | retrieval | 25/25 | 7/7 | 0.0 | 0.0 | 4 | Rủi ro truy xuất sai nghĩa vẫn còn | — |
| 25 cá nhân | llm (stub) | 25/25 | 7/7 | 0.1 | 0.2 | 3 | Citation hợp lệ chưa chứng minh nội dung đúng | — |

Latency do script làm tròn tới 0.1 ms; `0.0` không có nghĩa thời gian bằng không, và số đo stub không đại diện model thật.
Baseline deterministic được dựng với index rỗng; retrieval dùng index thật và `llm=None`.
Điểm đúng được tính theo `expect_source`, `expect_contains` hoặc `path == "abstain"`; không phải chấm đủ độ chính xác ngữ nghĩa.

## Lựa chọn đường xử lý — đúng 3 câu

Đối với câu hỏi quy định trong handbook, tôi chọn retrieval có ngưỡng và giữ tính học phí ở đường deterministic.
Trong lần chạy này, retrieval và stub đều đạt 20/20 rồi 25/25, còn retrieval trả thẳng đoạn nguồn và có ít bước phụ thuộc hơn.
Lỗi cần ưu tiên sửa tiếp là câu trả lời trích một ID hợp lệ nhưng nội dung chưa trả lời đúng ý hỏi, vì A2 chỉ kiểm ID thuộc tập được truy xuất.

## H1 — ba câu có nguồn, hai câu từ chối

Bộ cá nhân là **20 câu gốc + E26–E30**, lưu riêng ở `eval/cases_huy_25.jsonl`; cùng năm câu cũng được thêm vào `eval/cases.jsonl`, nâng bộ nhóm lên 45 câu.

| ID | Câu hỏi | Kỳ vọng | Kết quả retrieval / stub |
|---|---|---|---|
| E26 | Can I renew a library book online if another student has reserved it? | `S26#1` — chỉ gia hạn khi chưa có người đặt | Đúng nguồn; đoạn trả lời giữ điều kiện `if no one else has reserved them` |
| E27 | What is the minimum course content match for transfer credits? | `H26#8.3` — ít nhất 80 percent | Đúng nguồn, đoạn có điều kiện 80 percent |
| E28 | How long may I take a leave of absence? | `H26#8.1` — tối đa hai học kỳ | Đúng nguồn, đoạn có `up to two semesters` |
| E29 | What is the boiling point of ethanol? | `expect_abstain: true` | `abstain`, escalate=true, confidence=0.0 |
| E30 | What grade did my classmate get in physics? | `expect_abstain: true` | Privacy guard: `abstain`, escalate=false, confidence=0.0 |

Khi thêm E26–E30, retrieval và stub đều tăng từ 20/20 lên 25/25 với 7/7 câu từ chối đúng, còn deterministic trượt thêm E26/E27/E28 vì chế độ này không tìm quy định trong KB.

## Chạy lại từ root repo

```bash
source .venv/bin/activate
LLM_PROVIDER=stub RETRIEVAL_KIND=bm25 RETRIEVAL_MIN_SCORE=2.0 python eval/compare_paths.py --cases eval/cases_20.jsonl
LLM_PROVIDER=stub RETRIEVAL_KIND=bm25 RETRIEVAL_MIN_SCORE=2.0 python eval/compare_paths.py --cases eval/cases_huy_25.jsonl
LLM_PROVIDER=stub RETRIEVAL_KIND=bm25 RETRIEVAL_MIN_SCORE=2.0 python eval/compare_paths.py
```

Stdout nguyên bản: [20 câu](eval-20.txt), [25 câu](eval-25.txt), [45 câu](eval-45.txt).
[Metadata và SHA-256](evaluation-metadata.json) ghi cấu hình/commit/dataset; [75 response của ba chế độ](responses-25.json) lưu câu trả lời, path, confidence và nguồn thực tế.
