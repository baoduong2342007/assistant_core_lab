# Lab 3 — Before / After: Trần Quốc Huy

**Thành viên:** Trần Quốc Huy (`tqhuy0602`). **Phạm vi code:** config, `.env.example`, logging và tests liên quan.
Code nền đã có trong PR #1; branch này sửa và kiểm chứng phần của Huy, không nhận là tự viết toàn bộ package.

**Xác nhận cá nhân — 2026-10-26:** Huy xác nhận đã đọc, hiểu và đồng ý với 10 code smells
và ba phản hồi trong worksheet này. Nội dung vẫn được khai báo là có Codex hỗ trợ toàn bộ.
Issue [#12](https://github.com/baoduong2342007/assistant_core_lab/issues/12) đã đóng sau xác nhận.
PR owner [#19](https://github.com/baoduong2342007/assistant_core_lab/pull/19) được Dương approved
và merge tại `1ee4e9a3a5f6798722206b5b773c7f116d452080` ngày 2026-10-25.

Bảng và metrics dưới đây đo snapshot Core PR19, trước H1 và các sửa đổi knowledge về sau.
Ngày 2026-10-26, Codex đọc lại monolith cùng 11 file core bằng `git show 1ee4e9a:<path>` và
đo AST theo định nghĩa trong metrics.json: cả 12 entries đều khớp số tên gán, bare/broad except
và hàm dài nhất. Không dùng số đo cũ để mô tả mọi commit mới hơn.

## 10 hàng worksheet

| Câu hỏi | Monolith | Core sau thay đổi của Huy |
| --- | --- | --- |
| Đổi credit rate ở đâu? | Hằng `RATE` trong source; không chỉnh `RETAKE_RATE` khi chỉ đổi rate | `CREDIT_RATE_VND` qua `load_settings`; default < .env < environment; CLI override có sẵn |
| Test không internet/API key? | Stub vốn chạy offline, có random lỗi và sleep; `--test` chỉ in kết quả | Pytest assertions chạy offline; stub/template không cần key; lỗi provider có cờ kiểm soát |
| Thiếu handbook? | In lỗi rồi tiếp tục với dữ liệu thiếu | `DataError` ở startup, CLI exit 1; thuộc knowledge/service của đồng đội |
| Secret có bị in/log? | `llm()` in key giả và prompt khi DEBUG | Log request chỉ có event và metadata cho phép; key bị loại khỏi repr/model_dump; không log settings/full text |
| Tìm fee logic ở đâu? | Trong `handle()` nhiều trách nhiệm | `tools.py`; service chỉ điều phối (đây là cấu trúc nhóm) |
| Số tên gán ở module? | 9, gồm 3 container mutable | 4 trên toàn core: `__version__`, `__all__`, `GREETINGS`, `log`; config/logging không có tên gán cấp module |
| Bare `except:`? | 3 | 0; broad `except Exception` của config đã bỏ; broad catch trong knowledge vẫn thuộc Quyền |
| Hàm dài nhất? | `handle`: 56 dòng theo AST | `main`: 71 dòng; `service.handle`: 32 dòng. Tách trách nhiệm không đồng nghĩa mọi hàm đều ngắn hơn |
| Ruff issues? | 8 với E,F,I,B,UP,BLE, line length 120, isolated | Ruff check và BLE đạt trên source/tests; reference được giữ nguyên và exclude theo cấu hình nhóm |
| Đổi responder cần sửa service? | Gọi `llm()` trực tiếp | Inject responder qua constructor/protocol; chỉ provider offline stub/template được chấp nhận |

Đo trên file thực tế: [metrics.json](metrics.json), ngày 2026-10-25, Python 3.11.16/macOS.
Ba lần chạy monolith `--test` đều exit 0, có greeting/9.450.000 VND/Library/H26-5.3;
không quan sát thấy lỗi random trong ba lần này. Không xem đó là bằng chứng random failure đã được loại bỏ khỏi starter.

## Code smells và người xử lý

1. Key/config hard-code: Huy chuyển sang Settings/environment; starter giữ nguyên làm reference.
2. In key/prompt: Huy kiểm tra event JSON, không ghi full message hoặc key.
3. Print dùng làm logging: Huy đưa structured logs ra stderr; CLI giữ answer ở stdout.
4. Config bắt `Exception` quá rộng: Huy chỉ bọc lỗi đọc env và `ValidationError`, để programming errors nổi lên.
5. Handler bám stderr cũ: Huy thay handler do package sở hữu khi stream đổi, không nhân đôi handler.
6. Global mutable history/offices/handbook: Quyền/Dương quản lý dữ liệu và dependency injection.
7. `handle` gánh mọi việc: Dương điều phối qua module.
8. Tests chỉ in output: mỗi owner thêm assertions; Huy thêm config/logging cases.
9. Random lỗi/sleep: Bảo dùng deterministic stub.
10. Nối đường dẫn bằng chuỗi: Huy/Quyền dùng pathlib.

## Ba câu phản hồi — Huy đã đọc, hiểu và đồng ý ngày 2026-10-26

1. Cải thiện lớn nhất là lỗi config được phát hiện sớm mà không in giá trị environment, cùng log JSON tách khỏi câu trả lời.
2. Điểm phức tạp hơn là validation và quản lý handler phải xét môi trường test/nhúng thay stderr; đổi lại có tests bắt hồi quy.
3. Điều muốn cải tiến tiếp là context phiên do người dùng chọn để truy vết nhiều request; H1 đề xuất `--session-id` riêng vì `--log-level` đã có.

## AI usage

Người phụ trách code: **Trần Quốc Huy**. **Codex hỗ trợ toàn bộ**: đọc kế hoạch/code,
đề xuất và trực tiếp chỉnh code/tests/docs, chạy kiểm tra, đo metrics và chuẩn bị Git/PR.
Các thay đổi do AI tạo được giữ lại. Huy đã xác nhận worksheet như trên; xác nhận này không
đồng nghĩa H3 reading/reflection riêng hoặc thao tác nộp LMS đã hoàn tất.
