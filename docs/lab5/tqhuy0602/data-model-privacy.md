# H3 — Lưu trữ dữ liệu và quyền riêng tư

| Vấn đề trong `bad_schema.sql` | Hệ quả | Cách xử lý trong thiết kế Lab05 |
| --- | --- | --- |
| Mỗi dòng lưu lại tên, số điện thoại, toàn văn câu hỏi và câu trả lời | Tăng lượng dữ liệu cá nhân khi xem, sao lưu hoặc chia sẻ DB để phân tích | Ghi `intent`, mã chủ đề, kết quả và độ trễ trong `interaction`. |
| Gộp mọi thứ vào `chats`, thiếu định danh phiên và khóa chính có ràng buộc | Khó nhóm nhiều lượt hỏi cùng phiên hoặc truy vết feedback về đúng lượt hỏi | Dùng `chat_session.id` là hash có salt, `interaction.session_id` tham chiếu phiên và `interaction.request_id` duy nhất. |
| `feedback` là chuỗi như `1,-1,1` | Khó gắn thời điểm, lọc theo rating hoặc kiểm tra miền giá trị | Mỗi đánh giá có một dòng riêng trong `feedback` với `request_id`, `rating`, `created_at` và comment tùy chọn. Migration 001 có `CHECK` cho rating. |
| `latency` chứa chuỗi như `120ms` | Phải tách đơn vị và chuyển kiểu trước khi tính trung bình | Lưu `latency_ms` dưới dạng số thực. |

Giữ `SESSION_SALT` riêng tư và ổn định qua restart để các lượt hỏi tiếp tục được nhóm đúng. Hash vẫn cho phép liên kết các lượt hỏi cùng phiên. Comment feedback là văn bản tự do và có thể chứa thông tin nhận dạng. Dữ liệu demo dùng comment giả lập. Nếu triển khai với người dùng thật, nhóm cần quyết định thời hạn lưu comment và metadata phù hợp với mục đích sử dụng.
