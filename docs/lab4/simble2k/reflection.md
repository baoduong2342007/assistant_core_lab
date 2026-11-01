# Reflection — Lab 04

Ở Lab 3, việc tương tác với trợ lý học tập được thực hiện thông qua lời gọi hàm nội bộ `service.handle()` trong tiến trình Python cục bộ, phụ thuộc hoàn toàn vào môi trường runtime và mã nguồn core.
Ở Lab 4, ứng dụng được mở rộng qua giao thức HTTP mạng, cho phép client từ xa gửi request độc lập tới các endpoints mà không cần import hay phụ thuộc mã nguồn Python.
Dữ liệu gửi nhận được chuẩn hóa bằng định dạng JSON và được Pydantic schemas kiểm thực tự động, loại bỏ các dữ liệu rác hoặc sai cấu trúc trước khi chạm tới tầng nghiệp vụ.
Các mã trạng thái HTTP (200, 201, 401, 422, 503) cùng định dạng lỗi tiêu chuẩn giúp phía gọi phân biệt rõ ràng giữa thành công, lỗi tham số client, hay sự cố dịch vụ ngoại vi.
Giao diện REST API giúp phân tách rõ ràng trách nhiệm giữa backend và các nền tảng khác, cho phép đồng đội phát triển web, mobile app hoặc microservice bằng bất kỳ ngôn ngữ nào một cách dễ dàng.
