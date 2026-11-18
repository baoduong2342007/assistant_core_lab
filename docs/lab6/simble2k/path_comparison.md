# Bảng so sánh ba chế độ và đánh giá mở rộng Lab 06

- Người thực hiện: **Phạm Quốc Bảo** (`simble2k`)
- Nhánh: `feat/lab06-personal-simble2k`
- Mốc commit: `80b9d39` (kế thừa Lab 05 PR #44)
- Thiết lập: BM25 index, ngưỡng `retrieval_min_score=2.0`, provider `stub`

---

## 1. Kết quả chạy bộ 20 câu gốc (`eval/cases_20.jsonl`)

| Chế độ | Correct | Abstain OK | p50 latency (ms) | max latency (ms) | Case IDs thất bại |
|---|:---:|:---:|:---:|:---:|---|
| **Deterministic** | 7/20 | 5/5 | 0.0 | 0.3 | E01 E02 E05 E06 E07 E08 E09 E10 E11 E12 E13 E14 E15 |
| **Retrieval-only** | 20/20 | 5/5 | 0.0 | 0.1 | (không có) |
| **RAG / LLM (`stub`)** | 20/20 | 5/5 | 0.2 | 0.5 | (không có) |

---

## 2. Kết quả chạy bộ 25 câu mở rộng H1 (`eval/cases.jsonl`)

Bổ sung 5 câu hỏi cá nhân dải ID `E41–E45` của Bảo (3 câu có nguồn, 2 câu từ chối):
- `E41`: *"how many credits do I need to register for a thesis"* $\rightarrow$ nguồn `H26#5.3`
- `E42`: *"when must tuition be paid by"* $\rightarrow$ nguồn `F26#3`
- `E43`: *"how many days can I borrow books from the library"* $\rightarrow$ nguồn `S26#1`
- `E44`: *"where can I apply for an on-campus dorm room"* $\rightarrow$ `expect_abstain: true`
- `E45`: *"can I borrow a laptop from the library"* $\rightarrow$ `expect_abstain: true`

| Chế độ | Correct | Abstain OK | p50 latency (ms) | max latency (ms) | Case IDs thất bại |
|---|:---:|:---:|:---:|:---:|---|
| **Deterministic** | 9/25 | 7/7 | 0.0 | 0.5 | E01 E02 E05 E06 E07 E08 E09 E10 E11 E12 E13 E14 E15 E41 E42 E43 |
| **Retrieval-only** | 24/25 | 6/7 | 0.0 | 0.1 | E45 |
| **RAG / LLM (`stub`)** | 24/25 | 6/7 | 0.2 | 0.6 | E45 |

---

## 3. Ba câu phân tích theo yêu cầu Rubric

1. **Chế độ chọn cho handbook**: Tôi chọn chế độ **RAG / LLM kết hợp kiểm định căn cứ nguồn (A1 + A2)** làm đường dẫn chính cho việc tra cứu quy chế handbook.
2. **Lý do lựa chọn**: Chế độ này đạt độ chính xác cao nhất (24/25 câu), vừa trả lời mượt mà tự nhiên bằng ngôn ngữ người dùng, vừa bảo đảm an toàn khi kết hợp cơ chế phòng thủ đa tầng: A1 từ chối sớm câu hỏi ngoài phạm vi với 0 lần gọi LLM, A2 bắt buộc trích dẫn nguồn có thực trong tài liệu, và Fallback tự động giáng cấp trích dẫn chunk thô khi nhà cung cấp gặp sự cố.
3. **Lỗi ưu tiên sửa**: Tôi ưu tiên sửa lỗi của case **E45** (*"can I borrow a laptop from the library"*), trong đó BM25 ghép nhầm từ khóa *"borrow"* và *"library"* với quy định mượn sách (`S26#1`) vượt ngưỡng 2.0; giải pháp là bổ sung bộ lọc thực thể danh từ (entity checking) hoặc huấn luyện prompt để LLM chủ động từ chối (`abstain: true`) khi tài liệu chỉ quy định về sách mà không đề cập thiết bị laptop.

---

## 4. Giải thích chi tiết kết quả H1 và case fail

- Các câu hỏi có nguồn (`E41`, `E42`, `E43`) đạt điểm số BM25 rất cao (từ 4.5 đến 9.3) và trích xuất chính xác 100% mã chunk tương ứng.
- Câu hỏi ngoài phạm vi `E44` (*"on-campus dorm room"*) đạt điểm BM25 cao nhất là 1.906, thấp hơn ngưỡng `min_score=2.0`, do đó tầng A1 đã can thiệp từ chối thành công ngay lập tức mà không tốn chi phí gọi LLM.
- Case fail duy nhất là `E45`: đây là minh họa kinh điển cho hiện tượng điểm tương đồng bề mặt cao nhưng thiếu căn cứ ngữ nghĩa, khẳng định tầm quan trọng của việc kiểm tra nội dung thực tế thay vì chỉ tin tưởng vào điểm số của bộ tìm kiếm từ khóa.
