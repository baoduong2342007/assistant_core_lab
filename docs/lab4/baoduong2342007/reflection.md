Ở Lab03, chương trình Python gọi service.handle với một Message và nhận về Response.
Ở Lab04, client gửi yêu cầu HTTP đến endpoint để sử dụng lại service đó.
JSON trao đổi dữ liệu, còn Pydantic kiểm tra cấu trúc và giới hạn của đầu vào.
Mã trạng thái HTTP cùng nội dung phản hồi giúp client biết yêu cầu thành công hay có lỗi.
API cho phép frontend hoặc ứng dụng khác dùng chung chức năng mà không cần gọi trực tiếp mã Python.
