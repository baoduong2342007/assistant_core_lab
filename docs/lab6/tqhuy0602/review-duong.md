# Huy — kiểm tra kỹ thuật luồng tích hợp của Dương

Ngày 20/11/2026; Codex thực hiện theo yêu cầu của Huy, trên main `28729b8` đã merge PR #54 và các sửa tích hợp của nhóm.
Phạm vi: `service.py`, `__main__.py`, `assistant_api/main.py`, các test entry point và API/SQLite.
Đây là assisted review của bản main tích hợp, không phải review độc lập của Huy hoặc GitHub approval tại head PR #49.

Kết quả: không phát hiện lỗi chặn trong phạm vi đã kiểm; baseline 420 test đạt, bản bổ sung Huy 512 test đạt.
CLI và API dùng chung `build_service`; fixture chỉ có handbook JSON còn đi được đường legacy; override CLI lấy cả trường bị exclude nên không làm mất key/salt.
Guard chạy trước router khi bật RAG; học phí trả 9,450,000 VND cho E03, phòng thư viện B.201 cho E04, thẻ sinh viên có nguồn S26#3; A1 và API restart đã có test thật.
Các cờ list-rules/show-sources/fail-provider/credit-rate/session-id và các bài regression API/weather/rate limit đều nằm trong suite đã chạy.

Điểm cần bổ sung tìm thấy trong factory: trước thay đổi, RAG chỉ tạo StubLLM trực tiếp và settings từ chối Ollama/OpenAI dù adapter đã có trong module.
Commit `e970ec1` đã nối `make_llm` vào factory, thêm mock test xác nhận truyền đúng provider/model/base URL/key/timeout và giữ fail-provider offline; API đóng provider mà nó sở hữu khi shutdown.
Phần này là thay đổi tích hợp tối thiểu cần để adapter của Huy hoạt động qua entry point chung.

Giới hạn: kiểm tra local Python 3.11.16; chưa chạy model thật, CI nhánh hoặc Uvicorn restart bằng tiến trình riêng trong lần này.
Suite hiện có đã kiểm feedback qua hai lần tạo app trên cùng file SQLite; đây là bằng chứng test, không được mô tả thành demo Uvicorn thủ công.
