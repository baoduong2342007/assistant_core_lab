# Usability & QA Review Report — FIT Study Assistant (Lab 07 H1)

- **Ngày test:** 2026-11-25
- **Môi trường kiểm thử:** `http://192.168.1.35:8501/` (Streamlit UI, viewport `850x694`, Dark theme)
- **Nhánh đối chiếu:** `feat/lab07-personal-luongnhatinh` (`assistant_core_lab`)
- **Vai trò người test:** Reviewer UX/QA ngoài nhóm (trải nghiệm độc lập ~10 phút, không hướng dẫn thêm)
- **Hai nhiệm vụ được giao:**
  1. Kiểm tra với **118 tín chỉ** thì có đăng ký khóa luận (*thesis*) được không?
  2. Kiểm tra nếu bị **mất thẻ sinh viên** thì đến đâu để làm lại?

---

## 1. Kết quả hoàn thành 2 nhiệm vụ chính

| Nhiệm vụ | Thao tác | Thời gian phản hồi | Kết quả thực tế trên app | Đạt / Chưa đạt |
| :--- | :--- | :--- | :--- | :--- |
| **1a. Thesis với 118 tín chỉ (nút mẫu)** | Click sidebar `"Can I register my thesis with 118 credits?"` | ~2.7s (`2670 ms`) | `According to 5.3 Thesis registration: Students may register a thesis when they have at least 120 accumulated credits and a cumulative GPA of at least 2.0. Registration opens in week 1 and closes in week 3 of the semester.` · `Sources: H26#5.3 — 5.3 Thesis registration` | **Đạt một phần** (đúng quy định, nhưng không trả lời thẳng `"No / Chưa đủ"`) |
| **1b. Thesis với 118 tín chỉ (tự diễn đạt)** | Gõ `"I have 118 credits. Am I eligible for graduation thesis?"` | ~4.4s (`4398 ms`) | Trả về đúng quy định mục `5.3 Thesis registration` + `Sources: H26#5.3 — 5.3 Thesis registration`. | **Đạt một phần** |
| **2a. Mất thẻ sinh viên (hỏi tiếng Việt)** | Gõ `"Nếu bị mất thẻ sinh viên thì đến đâu để làm lại?"` | ~2.5s (`2525 ms`) | Rơi vào abstain/fallback: `"I'm not confident I can answer that from the official documents. Please contact the Training Office (room I.101) or ask your academic advisor."` + alert box `"I could not find this in the official documents. A staff member can help: Training Office, room I.101."` | **Thất bại & chỉ sai phòng ban** (đẩy về I.101 thay vì I.102) |
| **2b. Mất thẻ sinh viên (nút mẫu tiếng Anh)** | Click sidebar `"I lost my student card"` | ~1.3s (`1293 ms`) | `According to 3 Student card replacement: A lost student card can be replaced at Student Affairs (room I.102). The replacement fee is 50,000 VND and the new card is ready in 3 working days.` · `Sources: S26#3 — 3 Student card replacement` | **Đạt** |

---

## 2. Nhật ký kiểm thử mở rộng & Edge Cases

| STT | Kịch bản kiểm thử | Input / Thao tác | Thời gian | Phản hồi thực tế | Ghi chú vấn đề |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **E1** | Diễn đạt lại tiếng Anh tự nhiên (có chữ `"fee"` và `"student ID card"`) | Gõ `"Where do I go to reissue a misplaced student ID card, and how much is the fee?"` | ~2.8s (`2779 ms`) | `"How many credits?"` (không có nguồn) | Bị phân loại nhầm sang intent tính học phí (`Intent.FEE`). |
| **E2** | Hỏi nối tiếp ngữ cảnh hội thoại | Gõ `"What are their opening hours?"` ngay sau E1 | ~2.8s (`2805 ms`) | Trả về `2 IT account password reset` (`room E.005`, `Sources: S26#2`) | Không nhớ ngữ cảnh `"their"` và truy xuất sai chủ đề không liên quan. |
| **E3** | Tính học phí qua nút mẫu | Click `"Tuition for 18 credits and 2 retake"` | ~3.5s (`3483 ms`) | `"Your tuition is 9,450,000 VND."` (không có nguồn) | Đúng kết quả nhưng thiếu công thức / đơn giá giải trình. |
| **E4** | Hỏi văn phòng qua nút mẫu | Click `"Where is the library?"` | ~3.7s (`3691 ms`) | `"Library: room B.201, open Mon-Sat 07:00-20:00."` | Rõ ràng, ngắn gọn. |
| **E5** | Câu hỏi ngoài phạm vi | Gõ `"What is the campus Wi-Fi password?"` | ~4.4s (`4381 ms`) | Trả về `2 IT account password reset` (`Sources: S26#2`) | Bị khớp từ khóa `"password"`, không abstain. |
| **E6** | Nút đánh giá `👎` / `👍` | Click `👎 Not helpful` (câu tiếng Việt) và `👍 Helpful` (câu thẻ SV) | ~2.9s / ~2.7s | Hiện toast `"Thanks — we will look at this answer."` / `"Thanks for your feedback!"`, ẩn cả 2 nút ngay sau rerun. | Khi toast biến mất không còn dấu hiệu đã lưu feedback; toast che nhẹ góc trên phải khung chat. |
| **E7** | Thu gọn/mở lại sidebar & kiểm menu `⋮` | Click `<`, click `>`, mở menu `⋮` | Tức thì | Thu gọn/mở lại hoạt động tốt; menu `⋮` chỉ có `Rerun`, `Settings`, `Print`, `About`. | Nút `<` ẩn khi chưa hover; không có nút `Clear chat` / `New chat`; khi đã cuộn lên bấm feedback, các tin nhắn gửi sau không tự cuộn xuống đáy. |

---

## 3. Danh sách phát hiện theo mức độ ưu tiên

### Cao (Critical / High)
1. **Không hỗ trợ tiếng Việt & Fallback chỉ nhầm phòng ban:** Hỏi tiếng Việt cho câu hỏi mất thẻ sinh viên không tìm ra tài liệu và hướng dẫn nhầm sang `Training Office (room I.101)` thay vì `Student Affairs (room I.102)`, đồng thời giao diện không báo cho sinh viên biết hệ thống chỉ hỗ trợ tiếng Anh.
2. **Định tuyến sai do khớp từ khóa hẹp (`student ID card` + `fee`):** Câu `"Where do I go to reissue a misplaced student ID card, and how much is the fee?"` bị kéo vào nhánh tính học phí và trả lời `"How many credits?"`.
3. **Truy xuất lệch đề ở câu hỏi mơ hồ / ngoài phạm vi & không có ngữ cảnh hội thoại:** `"What are their opening hours?"` và `"What is the campus Wi-Fi password?"` đều trả về `2 IT account password reset (room E.005)`.

### Trung bình (Medium)
4. **Thông báo fallback bị lặp 2 lần trong cùng một lượt trả lời:** Văn bản chính (`ESCALATE_MSG`) và hộp `st.info(status_note(result))` cùng nói về việc không tìm thấy trong tài liệu và đẩy sang `Training Office, room I.101`.
5. **Mất tự động cuộn xuống cuối sau khi người dùng cuộn lên trên:** Sau khi cuộn lên bấm feedback, các câu trả lời mới ở dưới bị khuất ngoài viewport.
6. **Thiếu nút `New chat` / `Clear conversation`:** Người dùng không thể xóa nhanh lịch sử chat lỗi để bắt đầu phiên mới ngoài cách reload trang.
7. **Câu trả lời thiếu diễn giải trực tiếp:** Hỏi `"118 credits"` không trả lời thẳng `"No, you need at least 120 credits"`; hỏi học phí chỉ in tổng tiền `9,450,000 VND` không kèm công thức.
8. **Mã nguồn trích dẫn (`H26#5.3`, `S26#3`) thiếu giải thích và không tương tác được.**

### Nhỏ (Minor / Polish)
9. **Chính tả ở nút mẫu:** `"Tuition for 18 credits and 2 retake"` (thiếu `s` ở `retakes`).
10. **Feedback UX:** Hai nút `👍 Helpful` / `👎 Not helpful` hơi rộng; sau khi bấm biến mất hoàn toàn thay vì hiện trạng thái `"Feedback recorded"`; `st.toast` đè nhẹ lên bong bóng chat.
11. **Sidebar & Accessibility:** Sidebar chiếm `336px` (~40% ở màn hình `850px`), nút `<` ẩn khi chưa hover, các nút icon thiếu `aria-label`, placeholder ô nhập hơi mờ.

---

## 4. Ảnh minh chứng (`screenshots/before/`)

- [01_landing.png](screenshots/before/01_landing.png) — Màn hình khởi đầu (giao diện tiếng Anh hoàn toàn, typo `2 retake`, không có nút New chat).
- [02_thesis_118_credits.png](screenshots/before/02_thesis_118_credits.png) — Câu trả lời 118 tín chỉ trích nguyên văn mục `5.3 Thesis registration` (`H26#5.3`).
- [03_vietnamese_lost_card_fallback.png](screenshots/before/03_vietnamese_lost_card_fallback.png) — Hỏi tiếng Việt về mất thẻ sinh viên bị fallback lặp 2 lần và chỉ nhầm sang `Training Office, room I.101`.
- [04_english_lost_card.png](screenshots/before/04_english_lost_card.png) — Bấm nút tiếng Anh `"I lost my student card"` ra đúng `Student Affairs (room I.102)`, `50,000 VND`, `3 working days`.
- [05_paraphrase_fee_bug_and_toast.png](screenshots/before/05_paraphrase_fee_bug_and_toast.png) — Câu hỏi paraphrase tiếng Anh có `"student ID card"` + `"fee"` trả về `"How many credits?"`; toast feedback đè góc bong bóng chat.
- [06_feedback_hidden_and_scroll_clip.png](screenshots/before/06_feedback_hidden_and_scroll_clip.png) — Nút feedback biến mất hoàn toàn sau khi vote và tin nhắn mới bị khuất dưới đáy khung nhìn do không tự cuộn lại.
