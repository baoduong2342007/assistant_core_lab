# Bàn giao Lab 06 — Trần Quốc Huy (`tqhuy0602`)

Ngày 20/11/2026, Asia/Ho_Chi_Minh. Nhánh: `feat/lab06-personal-tqhuy0602`, tạo từ main `28729b8`.
Code đã kiểm: `e970ec1d2c09eb04417557c2ac0e9baa11074349`.

## Phần hoàn thành

- Settings nhận `stub`, `template`, `ollama`, `openai`; validate URL/model/timeout/retrieval/prompt và yêu cầu key cho OpenAI; `.env.example` có `LLM_BASE_URL` cùng hướng dẫn mặc định offline.
- Giữ precedence defaults < dotenv < environment; key/salt bị loại khỏi repr và serialization; test CLI override xác nhận ba secret vẫn được giữ trong Settings nội bộ.
- Adapter có thể nhận MockTransport; HTTP lỗi, JSON hỏng, envelope sai, content không phải chuỗi đều thành ProviderError; retry hai lượt rồi trả top hit với degraded=true.
- A2 nhận citation hợp lệ của lượt hiện tại, chặn tập ID lẫn nguồn lạ, chặn schema sai/field dư/coercion; abstain có thể thiếu source_ids; thông báo lỗi không chép nội dung provider.
- Prompt ghi rõ điều kiện nguồn/abstain; thay placeholder một lượt để không sửa các chuỗi `{question}`/`{sources}` nằm trong dữ liệu; version prompt bị giới hạn.
- Factory dùng adapter được chọn cho cả CLI/API; `--fail-provider` vẫn mô phỏng offline; API đóng HTTP provider do nó sở hữu khi shutdown.
- H1 có E26–E30 đúng tỉ lệ 3 có nguồn + 2 từ chối, bộ cá nhân 25 câu riêng và bộ nhóm 45 câu; có bảng 20/25 câu, ba câu phân tích và reflection H2 đúng năm dòng.

## S1–S3/A1–A2 và nguồn kế thừa

Main tại thời điểm bắt đầu đã có mini search, A1, A2, KB và evaluator của nhóm; baseline chạy lại là **420 passed**, không nhận chúng là code mới của Huy.
Để có lời giải thực hành có thể kiểm tra riêng, [starter_solution.patch](starter_solution.patch) được tạo trên đúng học liệu `11d934ccf8de9b0cf057d69afd84f2e2cf343dc9`, sửa đúng ba đường dẫn `practice/mini_search.py`, `src/assistant_core/llm.py`, `src/assistant_core/rag/answerer.py`.
[Log trước/sau](starter-tests.txt): mini search **2 pass/2 fail → 4 pass**, starter **40 pass/2 fail → 42 pass**; [manifest](exercise-provenance.json) ghi hash trước/sau của ba file.
Patch là bài tập tối thiểu trên starter; code production trong commit bàn giao có thêm validation strict và xử lý HTTP phù hợp repo nhóm.

Để áp dụng patch: export `lab06/starter` của commit học liệu nói trên, chép `lab06/practice` vào `starter/practice`, chạy `git apply /duong-dan/starter_solution.patch` tại root starter rồi chạy hai lệnh pytest tương ứng trong log.
Không cần áp dụng patch vào repo nhóm vì các TODO đã được main hoàn thành trước đó.

## Kiểm chứng bản tích hợp

| Gate | Kết quả |
|---|---|
| `python -m pytest -q` | 512 passed (92 test mới so với baseline) |
| `python -m pytest -q practice/test_mini_search.py` | 4 passed |
| `python -m pytest -q practice/test_hello_api.py practice/test_school_repo.py` | 10 passed |
| `python practice/make_school_db.py` rồi `python practice/check.py` | 15/15 |
| Ruff lint / format / BLE | Đạt |
| `python -m build --no-isolation` | sdist + wheel thành công |
| Wheel cài trong venv sạch, chạy từ `/private/tmp` với Python `-I` | Import từ site-packages, có prompt, stub trả S26#3 và không tạo HTTP client |
| Bộ 20 / 25 / 45 câu | retrieval và stub: 20/20, 25/25, 45/45 |

Log: [tests.txt](tests.txt), [build.txt](build.txt), [wheel-smoke.json](wheel-smoke.json), [bảng cá nhân](path_comparison.md).
Python local là 3.11.16; trạng thái GitHub CI trên Python 3.10/3.12 được theo dõi tại [PR #55](https://github.com/baoduong2342007/assistant_core_lab/pull/55/checks).
Cảnh báo duy nhất của pytest đến từ deprecated alias của dependency Starlette/AnyIO.
Ollama/OpenAI mới được kiểm bằng mock; chưa gọi model thật hoặc thực hiện bonus.

Một test cũ trong `tests/test_config.py` đổi provider giả từ `openai` thành `unsupported`, vì OpenAI nay là provider hợp lệ; yêu cầu từ chối provider không hỗ trợ vẫn được giữ và trường hợp OpenAI thiếu key được kiểm riêng.
Package data `prompts/*.txt` đã có trong main, được giữ nguyên và kiểm bằng wheel; không nhận là khai báo mới.

## AI, review và trạng thái gửi bài

Codex hỗ trợ toàn bộ code, test, patch bài tập, phép đo và tài liệu trong lần làm này theo yêu cầu của Huy.
[reflection.md](reflection.md) là bản nháp do AI soạn đúng năm dòng, chưa có xác nhận Huy tự viết hoặc đã đọc/diễn đạt lại.
[review-duong.md](review-duong.md) là kiểm tra kỹ thuật có AI hỗ trợ trên bản tích hợp, chưa phải peer approval trên GitHub.

Mã và hồ sơ đã push trên nhánh cá nhân, với [PR draft #55](https://github.com/baoduong2342007/assistant_core_lab/pull/55) mở bằng tài khoản `tqhuy0602`; [pr-body.md](pr-body.md) lưu nội dung PR.
Chưa có review của Quyền, chưa nộp LMS hoặc tạo tag `v0.6-ai`; không tự đánh dấu các bước này hoàn thành.
