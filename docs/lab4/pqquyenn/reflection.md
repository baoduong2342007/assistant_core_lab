# Reflection — Lab 04

Ở Lab 3, hệ thống hoạt động hoàn toàn dưới dạng lời gọi hàm nội bộ `service.handle()` trong cùng tiến trình Python, khiến client bị gắn chặt vào thư viện mã nguồn và môi trường runtime máy cục bộ.
Sang Lab 4, việc mở rộng `service.handle()` qua endpoint `POST /v1/chat` và giao thức HTTP biến trợ lý thành một dịch vụ mạng độc lập, cho phép gọi từ xa qua chuẩn mạng Internet.
Dữ liệu gửi nhận qua HTTP được cấu trúc bằng JSON và kiểm thực tự động qua Pydantic models, giúp ngăn chặn dữ liệu rác hay khoảng trắng trước khi đưa vào xử lý nghiệp vụ lõi.
Các mã trạng thái HTTP như 200, 201, 401, 422, 429 và 503 giúp chuẩn hóa phản hồi, phân định rành mạch giữa thành công, lỗi dữ liệu đầu vào phía client, hay lỗi hạ tầng từ chối phục vụ.
Nhóm phát triển ưu tiên giao diện HTTP backend vì tính linh hoạt và tách biệt giao diện: các thành viên làm web frontend, mobile hay desktop app bằng bất kỳ ngôn ngữ nào đều có thể tích hợp mượt mà mà không phụ thuộc mã nguồn Python của core.
