# H3 — Trần Quốc Huy (`tqhuy0602`)

**Trạng thái:** bản nháp có Codex hỗ trợ; chưa xác nhận Huy đã tự đọc hoặc tự hoàn thành reflection.

## Reading và ví dụ từ code thực tế

- [I — Codebase](https://12factor.net/codebase): một codebase có lịch sử Git cho mỗi ứng dụng. Core dùng repo `assistant_core_lab`; bootcamp là bài riêng. Branch/PR và SHA giúp truy nguồn thay đổi config/logging.
- [II — Dependencies](https://12factor.net/dependencies): khai báo và cô lập dependencies. `pyproject.toml` khai báo runtime ranges; `requirements.txt` pin các dependency trực tiếp, `.venv` cô lập môi trường. Transitive dependencies chưa được lock toàn bộ nên không tuyên bố build hoàn toàn tái lập.
- [III — Config](https://12factor.net/config): starter đặt key giả và rate trong source, khiến config phải sửa bằng code. `config.py` đọc environment và .env với `override=False`, validate miền/kiểu và chỉ chấp nhận stub/template. .env được ignore; .env.example không có credential.
- [XI — Logs](https://12factor.net/logs): starter in key/prompt và trộn debug với output. `logging_setup.py` dùng JSON event, whitelist metadata và stderr; `process_message` ghi handled/intent/latency/session/degraded. XII-factor mô tả stdout cho event streams; lab dùng stderr để giữ stdout dành cho answer/JSON. Không xem lựa chọn stream này là trích nguyên yêu cầu XII-factor.
- [Packaging Python Projects](https://packaging.python.org/en/latest/tutorials/packaging-projects/): metadata nằm ở `pyproject.toml`, package dùng src layout và editable install. Tên distribution `assistant-core` khác tên import `assistant_core`; không cần publish PyPI để hoàn thành lab.

## Reflection dựa trên thay đổi hiện tại

Vi phạm rõ nhất trong phần Huy là config/secret ở source và debug in key/prompt. `repr=False` chỉ ẩn repr,
không bảo vệ serialization; thay đổi thêm `exclude=True`, không dump settings ra logs, và tests dùng secret/message giả
để kiểm tra đúng đường xuất log. Key vẫn là chuỗi trong bộ nhớ, nên không tuyên bố mọi cách truy cập đều được che.

Tách module có chi phí: phải thống nhất Settings, ConfigError, thứ tự override và log event schema.
Ở bài này chi phí đó có ích vì có thể kiểm tra config độc lập bằng tmp .env và kiểm tra logging bằng stream riêng,
không gọi provider/network. Handler setup phải chịu được stderr đổi giữa các lần chạy và vẫn giữ handler của ứng dụng nhúng.

Hàm CLI `main` vẫn dài 71 dòng trong snapshot core; việc chia module đã làm ranh giới trách nhiệm rõ hơn,
nhưng không đủ cơ sở để ghi mọi hàm đều ngắn đi hoặc toàn core không còn globals.

## Huy cần hoàn tất trực tiếp

- Tự đọc các nguồn trên, đối chiếu các ví dụ với code.
- Viết lại/xác nhận nhận xét theo hiểu biết của mình và giải thích validation, override, stream/handler ownership.
- Xác nhận giờ làm thực tế và việc nộp trên LMS; không có xác nhận này từ phiên tự động.

## AI usage

Code/phần việc do **Trần Quốc Huy phụ trách**; **Codex hỗ trợ toàn bộ**, gồm đề xuất/chỉnh code,
viết bản nháp reflection, đọc nguồn và chạy tests. Việc đọc và tự phản ánh cá nhân đang chờ Huy xác nhận.
