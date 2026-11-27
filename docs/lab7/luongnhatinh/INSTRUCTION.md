# Instruction cho người thực hiện — Hoàn thiện Lab 07 (H1 & UX Fixes)

Tài liệu này hướng dẫn người làm (dev hoặc coding agent) trên nhánh `feat/lab07-personal-luongnhatinh` sử dụng kết quả test thực tế của reviewer ngoài nhóm ngày **2026-11-25** để hoàn tất **H1 trong rubric Lab 07** và xử lý các vấn đề UX/routing đã phát hiện.

---

## 1. Tài liệu & minh chứng đã chuyển vào thư mục làm việc

Toàn bộ tài liệu test nằm trong `docs/lab7/luongnhatinh/`:

- Báo cáo chi tiết buổi test: `docs/lab7/luongnhatinh/usability_review_report.md`
- Ảnh chụp trạng thái **trước khi sửa (`before`)**:
  - `docs/lab7/luongnhatinh/screenshots/before/01_landing.png`
  - `docs/lab7/luongnhatinh/screenshots/before/02_thesis_118_credits.png`
  - `docs/lab7/luongnhatinh/screenshots/before/03_vietnamese_lost_card_fallback.png`
  - `docs/lab7/luongnhatinh/screenshots/before/04_english_lost_card.png`
  - `docs/lab7/luongnhatinh/screenshots/before/05_paraphrase_fee_bug_and_toast.png`
  - `docs/lab7/luongnhatinh/screenshots/before/06_feedback_hidden_and_scroll_clip.png`
- Các file Lab 07 cần cập nhật sau khi sửa:
  - `docs/lab7/luongnhatinh/user_test_observations.md` (hiện vẫn giữ bản trống theo ghi chú trong `status.md`)
  - `docs/lab7/luongnhatinh/status.md`

---

## 2. Ràng buộc quan trọng (KHÔNG làm vỡ test hiện có)

Trước khi sửa bất kỳ dòng nào, lưu ý các contract đang được `tests/test_ui.py` và `tests/test_ui_app.py` kiểm tra chặt:

1. **`ui/logic.py`:**
   - `validate_input("   ")` phải trả về đúng `"Please type a question."`.
   - `validate_input("x" * 2001)` phải bắt đầu bằng `"Your question is too long"`.
   - `format_sources(...)` phải giữ đúng format `"Sources: <id> — <title>"` (nối bằng `"; "` nếu nhiều nguồn, `""` nếu rỗng).
   - `status_note(ChatResult(ok=True, escalate=True))` phải chứa `"Training Office"` và `"I.101"`, và khi cả `escalate=True` lẫn `degraded=True` thì **không** chứa `"unavailable"`.
2. **`ui/app.py`:**
   - `tests/test_ui_app.py` kiểm tra sau khi bấm nút sidebar đầu tiên (`EXAMPLES[0]`), `len(at.chat_message) == 3` (welcome + user + assistant) và `ask` được gọi đúng 1 lần với `EXAMPLES[0]`.
   - `tests/test_ui_app.py` kiểm tra sau khi bấm `"👍 Helpful"` hoặc `"👎 Not helpful"`, hai nút này **không còn** trong `at.button`, có đúng 1 `at.toast` chứa `"Thanks"`, và không gửi lại feedback khi rerun.
   - Không đổi label hai nút `"👍 Helpful"` và `"👎 Not helpful"`, vì `test_ui_app.py` tìm nút theo đúng chuỗi label này.
3. **Backend (`src/assistant_core/`):**
   - Nếu có chỉnh backend, phải đảm bảo `eval/compare_paths.py` vẫn đạt `20/20` (`cases_20.jsonl`) và `45/45` (`cases.jsonl`), đồng thời toàn bộ unit/integration tests hiện có vẫn xanh.

---

## 3. Kế hoạch sửa đề xuất

### A. Commit bắt buộc cho H1 (Chỉ sửa tầng UI — an toàn, đúng phạm vi Lab 07)

Mục tiêu của **H1** là thực hiện **1 thay đổi UI có giá trị thật** xuất phát từ quan sát test, kèm **1 commit** và **ảnh Before/After** cùng kích thước cửa sổ và cùng câu hỏi.

Đề xuất gộp gọn các cải thiện UI tương thích test sau vào `ui/logic.py` và `ui/app.py` (tập trung giải quyết các lỗi thấy rõ trong `03_vietnamese_lost_card_fallback.png` và `06_feedback_hidden_and_scroll_clip.png`):

1. **Làm rõ ngôn ngữ hỗ trợ (English-only) & tránh lặp thông báo escalate gây hiểu nhầm:**
   - **Vấn đề:** Khi người dùng gõ tiếng Việt (*"Nếu bị mất thẻ sinh viên thì đến đâu để làm lại?"*), hệ thống không hiểu tiếng Việt nên escalate về `Training Office, room I.101`, đồng thời hiển thị **2 thông báo lặp nhau** (đoạn text của `result.answer` + hộp `st.info(status_note)`), khiến người dùng tưởng quy định không tồn tại hoặc đi nhầm phòng ban.
   - **Cách sửa ở `ui/logic.py` & `ui/app.py`:**
     - Cập nhật `WELCOME` và placeholder `st.chat_input(...)` nêu rõ hỗ trợ tiếng Anh (ví dụ: `"Ask in English about fees, offices or the handbook…"`).
     - Thêm helper nhận diện câu hỏi có dấu tiếng Việt / ký tự non-ASCII trong `ui/logic.py` (ví dụ `looks_non_english(text: str) -> bool`). Khi `result.escalate` là `True` và câu hỏi của user có tiếng Việt, nối thêm gợi ý ngắn trong hộp note của UI: `"Note: Official documents are currently indexed in English only — try rephrasing your question in English."` (lưu ý vẫn giữ nguyên giá trị trả về của `status_note(result)` để `tests/test_ui.py` pass 100%, hoặc chỉ bổ sung dòng gợi ý ở `ui/app.py` khi render).
     - Khi render tin nhắn escalate trong `ui/app.py`: tránh in lặp nội dung giống hệt nhau — nếu `result.escalate` là `True` và `m["content"]` đã chứa `"Training Office"`, có thể hiển thị gọn phần `st.info(...)` chỉ khi cần bổ sung thông tin mới (như gợi ý tiếng Anh) hoặc phân tách rõ câu trả lời chính với hộp hướng dẫn liên hệ, miễn không phá `AppTest`.
2. **Hiển thị xác nhận đã gửi feedback & thêm nút `New chat`:**
   - **Vấn đề:** Sau khi bấm `👍 Helpful` / `👎 Not helpful`, nút biến mất hoàn toàn (`feedback_slot.empty()`), nên sau khi toast tắt người dùng không thấy trạng thái đã đánh giá; ngoài ra không có nút xóa lịch sử chat.
   - **Cách sửa ở `ui/app.py`:**
     - Trong nhánh `else` của `if rid not in st.session_state.rated:`, thay `feedback_slot.empty()` bằng `feedback_slot.caption("✓ Feedback recorded")` (tương thích 100% với `test_ui_app.py` vì test chỉ assert hai nút không còn trong `at.button`).
     - Thêm nút `"New chat"` ở cuối `st.sidebar` để reset `st.session_state.messages = [{"role": "assistant", "content": WELCOME}]`, `st.session_state.rated = set()`, cấp `session_id` mới và `st.rerun()`. (Kiểm tra lại `test_ui_app.py`: test click `at.sidebar.button[0]` nên đặt `"New chat"` **sau** danh sách `EXAMPLES` hoặc dùng `key="new_chat"` để `sidebar.button[0]` vẫn là `EXAMPLES[0]`).
3. **Sửa lỗi chính tả nhỏ ở `EXAMPLES[1]` (tuỳ chọn):**
   - Trong `ui/logic.py`, cân nhắc sửa `"Tuition for 18 credits and 2 retake"` → `"Tuition for 18 credits and 2 retakes"`. Lưu ý kiểm tra `src/assistant_core/tools.py` (`re.search(r"(\d+)\s*retake", ...)` vẫn match `"2 retakes"`) và đảm bảo không test nào trong `tests/` hardcode chuỗi cũ của `EXAMPLES[1]`.

### B. Fix Backend khuyến nghị (Làm ở commit/PR riêng nếu team đồng ý chạm `src/assistant_core/`)

> Lưu ý: Chỉ sửa phần này nếu nằm trong phạm vi cho phép của nhánh/PR nhóm, tránh làm lệch mốc Lab 06 của team.

1. **`src/assistant_core/router.py` (dòng 26):**
   - Hiện tại: `if "student card" in t and re.search(r"\b(?:fees?|cost|replacement)\b", t):`
   - Lỗi thực tế: `"Where do I go to reissue a misplaced student ID card, and how much is the fee?"` không chứa `"student card"` liền nhau mà là `"student id card"`, nên rơi xuống `if "fee" in t or "tuition" in t: return Intent.FEE` → trả về `"How many credits?"`.
   - Cách sửa: dùng regex `re.search(r"\bstudent(?:\s+id)?\s+card\b", t)` và mở rộng động từ `reissue|replace|replacement|lost|fees?|cost`.
2. **`src/assistant_core/rag/answerer.py` & `src/assistant_core/rag/index.py`:**
   - Câu hỏi ngoài phạm vi `"What is the campus Wi-Fi password?"` khớp từ `"password"` với `S26#2` (`2 IT account password reset`) thay vì abstain. Cần siết evidence/threshold hoặc kiểm tra tỷ lệ từ khóa khớp khi câu chứa từ khóa ngoại lai (`wi-fi`).

---

## 4. Quy trình thực hiện từng bước cho người làm

1. **Đọc kỹ bằng chứng trước khi code:**
   - Mở `docs/lab7/luongnhatinh/usability_review_report.md` và xem 6 ảnh trong `docs/lab7/luongnhatinh/screenshots/before/`.
2. **Cài/sửa thay đổi UI (Mục 3A) và viết test bổ sung:**
   - Sửa `ui/logic.py` và `ui/app.py`.
   - Bổ sung unit test / `AppTest` trong `tests/test_ui.py` và `tests/test_ui_app.py` cho hành vi mới (ví dụ: hint tiếng Anh khi query có dấu tiếng Việt + escalate, caption `"✓ Feedback recorded"`, nút `"New chat"`).
3. **Chạy toàn bộ kiểm tra tự động:**
   ```powershell
   .venv\Scripts\python.exe -m pytest -q tests/test_ui.py tests/test_ui_app.py
   Push-Location practice; ..\.venv\Scripts\python.exe -m pytest -q test_hello_streamlit.py; Pop-Location
   .venv\Scripts\python.exe -m pytest -q
   .venv\Scripts\ruff.exe check .
   .venv\Scripts\ruff.exe format --check .
   .venv\Scripts\ruff.exe check --select BLE .
   ```
   *(Nếu có đụng `src/assistant_core/`, chạy thêm `eval/compare_paths.py` với `LLM_PROVIDER=stub`.)*
4. **Chụp ảnh `after` cùng điều kiện với `before`:**
   - Chạy lại 2 server (API + Streamlit).
   - Mở trình duyệt ở cùng kích thước cửa sổ (`850x694`, hoặc kích thước chuẩn bạn chọn cho cả cặp `before`/`after`), thực hiện lại đúng các kịch bản:
     - Gõ `"Nếu bị mất thẻ sinh viên thì đến đâu để làm lại?"` (so sánh với `screenshots/before/03_vietnamese_lost_card_fallback.png`).
     - Bấm `"👍 Helpful"` (so sánh với `screenshots/before/06_feedback_hidden_and_scroll_clip.png`).
   - Lưu ảnh mới vào `docs/lab7/luongnhatinh/screenshots/after/`.
5. **Commit fix và điền hoàn chỉnh worksheet H1:**
   - Tạo commit rõ ràng cho bản sửa H1 trên nhánh `feat/lab07-personal-luongnhatinh`.
   - Điền đầy đủ `docs/lab7/luongnhatinh/user_test_observations.md`:
     - Tester: `Outside Reviewer (AI UX/QA)`, Date: `2026-11-25`.
     - Chọn **3 quan sát tiêu biểu nhất** từ `usability_review_report.md` (gợi ý: (1) Hỏi tiếng Việt mất thẻ sinh viên bị fallback chỉ nhầm phòng I.101 & lặp thông báo; (2) Câu hỏi tiếng Anh có `"student ID card"` + `"fee"` bị hiểu nhầm sang `"How many credits?"`; (3) Nút feedback biến mất không dấu vết sau khi vote / hỏi nối tiếp `"their opening hours"` mất ngữ cảnh).
     - Gắn link/SHA commit và đường dẫn cặp ảnh `before` / `after`.
   - Cập nhật trạng thái hoàn thành H1 trong `docs/lab7/luongnhatinh/status.md`.
