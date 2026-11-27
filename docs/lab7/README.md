# Lab 07 — Hồ sơ nhóm

Bản MVP đầu tiên được phát hành tại `9feb9a5`. PR tích hợp ban đầu đưa một bản Streamlit lên `main`, dùng FastAPI qua HTTP và lưu feedback bằng SQLite. [PR tích hợp #58](https://github.com/baoduong2342007/assistant_core_lab/pull/58) · [Tag v0.7-mvp](https://github.com/baoduong2342007/assistant_core_lab/tree/v0.7-mvp)

## Bài cá nhân

Cả năm PR có mã warm-up U1–U4, luồng L1/L2/F1, kiểm thử và checklist. Ảnh và nhật ký demo ghi nhận kiểm thử kỹ thuật. Trạng thái bài thực hành theo hồ sơ ngày 27/11/2026.

| Thành viên | PR cá nhân | Kết quả kỹ thuật | Checklist | H1 | H2 |
| --- | --- | --- | --- | --- | --- |
| Dương | [#59](https://github.com/baoduong2342007/assistant_core_lab/pull/59) | [D.4 và test](baoduong2342007/demo_results.md) | [10 mục](baoduong2342007/usability_checklist.md) | [Chờ buổi thử](baoduong2342007/user_test_observations.md) | [Bản nháp hai câu](baoduong2342007/reading.md) |
| Huy | [#56](https://github.com/baoduong2342007/assistant_core_lab/pull/56) | [D.4 và test](tqhuy0602/demo_results.md) | [10 mục](tqhuy0602/usability_checklist.md) | [Chờ buổi thử](tqhuy0602/user_test_observations.md) | [Bản nháp hai câu](tqhuy0602/reading.md) |
| Minh | [#57](https://github.com/baoduong2342007/assistant_core_lab/pull/57) | [Test và trạng thái](luongnhatinh/status.md) | [10 mục](luongnhatinh/usability_checklist.md) | [Có buổi đánh giá AI, chờ người thử thật](luongnhatinh/user_test_observations.md) | [Bản nháp hai câu](luongnhatinh/reading.md) |
| Quyền | [#60](https://github.com/baoduong2342007/assistant_core_lab/pull/60) | [D.4 và test](pqquyenn/demo_results.md) | [10 mục](pqquyenn/usability_checklist.md) | [Chờ buổi thử](pqquyenn/user_test_observations.md) | [Bản nháp hai câu](pqquyenn/reading.md) |
| Bảo | [#61](https://github.com/baoduong2342007/assistant_core_lab/pull/61) | [D.4 và test](simble2k/demo_results.md) | [10 mục](simble2k/usability_checklist.md) | [Chờ buổi thử](simble2k/user_test_observations.md) | [Bản nháp hai câu](simble2k/reading.md) |

### Phần từng thành viên xác nhận

1. Mời một người ngoài nhóm thử khoảng 10 phút. Giao nhiệm vụ kiểm tra điều kiện đăng ký khóa luận với 118 tín chỉ và tìm nơi cấp lại thẻ sinh viên. Quan sát khi họ tự thao tác. Ghi ba hiểu nhầm do UI hoặc hệ thống vào worksheet, sửa một vấn đề từ ghi chép và thêm link commit cùng ảnh trước/sau chụp với cùng câu hỏi và kích thước cửa sổ.
2. Đọc hai chương PAIR khoảng 15 phút. Xác nhận hai câu trên PR cá nhân gồm một ý đã dùng và một ý muốn thêm vào một luồng cụ thể. [Feedback + Control](https://pair.withgoogle.com/guidebook-v2/chapter/feedback-controls/) · [Errors + Graceful Failure](https://pair.withgoogle.com/guidebook-v2/chapter/errors-failing/)
3. Cập nhật PR cá nhân đang mở để giữ lịch sử bài làm, minh chứng và ghi nhận hỗ trợ AI.

## Thay đổi tích hợp sau MVP

- Dương ghép nút **New chat** từ Minh và Quyền vào UI chung. Nút tạo phiên mới, xóa lịch sử và trạng thái feedback trên màn hình. Các feedback đã lưu vẫn tồn tại trong SQLite. [Minh #57](https://github.com/baoduong2342007/assistant_core_lab/pull/57) · [Quyền #60](https://github.com/baoduong2342007/assistant_core_lab/pull/60)
- Lời chào khuyên hỏi bằng tiếng Anh để có kết quả tốt hơn. Bản UI dùng ghi nhận feedback bền qua rerun và giữ nguyên quy tắc nguồn/escalation của MVP. [Minh #57](https://github.com/baoduong2342007/assistant_core_lab/pull/57) · [Huy #56](https://github.com/baoduong2342007/assistant_core_lab/pull/56)
- Kiểm thử tích hợp xác nhận cả hai mức đánh giá còn sau khi tạo lại FastAPI với cùng file SQLite. Phần phân nhóm nguồn của Bảo nằm trong PR cá nhân, theo thứ tự làm bonus của kế hoạch. [Bảo #61](https://github.com/baoduong2342007/assistant_core_lab/pull/61)

## Kiểm thử bản tích hợp

- Windows và Python 3.12.14 đạt 581 test ở thư mục gốc, 18 test practice gồm 4 warm-up và toàn bộ kiểm tra Ruff.
- Chrome kiểm D.4 trên FastAPI và Streamlit, gồm màn hình 375 px, mất kết nối, feedback thất bại rồi thử lại và lưu hai lượt đánh giá qua restart. Kiểm tra thêm việc mở phiên mới bằng New chat, xác nhận nút không gửi thêm câu hỏi và hai lượt đánh giá vẫn tồn tại.
