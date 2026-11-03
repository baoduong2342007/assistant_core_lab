# Reflection — Lab 04

Ở Lab 3, việc gọi trực tiếp `service.handle()` là lời gọi hàm nội bộ (in-process function call) bằng ngôn ngữ Python trên cùng một máy, phụ thuộc chặt chẽ vào mã nguồn và môi trường runtime của core.
Ở Lab 4, client gửi HTTP request đến `POST /v1/chat`, biến lời gọi hàm thành một network API độc lập thông qua giao thức chuẩn Internet.
Dữ liệu trao đổi qua HTTP được định dạng bằng JSON và kiểm thực nghiêm ngặt bằng Pydantic models, giúp chuẩn hóa request/response và tự động xử lý các lỗi cú pháp/kiểu dữ liệu.
Kết quả trả về kèm các HTTP status codes (200, 422, 503) giúp thông báo rõ ràng trạng thái thành công, lỗi dữ liệu từ phía client hoặc lỗi dịch vụ từ phía server.
Nhóm phát triển ưu tiên giao diện HTTP vì tính tách biệt (decoupling): các thành viên làm web frontend, mobile app hoặc backend service khác bằng bất kỳ ngôn ngữ nào đều có thể kết nối dễ dàng mà không cần cài đặt hay phụ thuộc mã Python nội bộ.
