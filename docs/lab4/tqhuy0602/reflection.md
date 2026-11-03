Trong Lab03, một chương trình Python tạo Message và gọi trực tiếp service.handle() để nhận Response.
Trong Lab04, client gửi HTTP đến endpoint, rồi API chuyển nội dung JSON thành Message cho cùng service xử lý.
JSON là dữ liệu trao đổi giữa client và server, còn Pydantic kiểm tra kiểu và giới hạn của các trường trước khi gọi core.
Response JSON mô tả kết quả; status 200/201 báo thành công, còn 401/422/503 giúp client phân biệt lỗi xác thực, dữ liệu và dịch vụ ngoài.
Giao diện HTTP giúp frontend hoặc mobile dùng lại nghiệp vụ mà không cần import code Python, nhưng vẫn phải xử lý lỗi mạng và dữ liệu cache cũ.
