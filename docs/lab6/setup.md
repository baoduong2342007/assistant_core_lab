# Lab 06 — thiết lập và giao diện nhóm

Mốc main: `80b9d3946ccc88d9a9eca21d9840432b3aee0db4`; học liệu gốc tại commit `11d934ccf8de9b0cf057d69afd84f2e2cf343dc9` của `CSC10014-at-fit-hcmus/public_materials`. Nhánh này là bài cá nhân Dương có lời giải; mỗi người tạo nhánh cá nhân từ mốc main, tự thực hành và lưu bằng chứng riêng. Chưa coi nhánh này là bản tích hợp đã được nhóm review.

Tại root repo với Python 3.12:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip install -e .
python -m pytest -q
python -m pytest -q practice/test_mini_search.py
python eval/compare_paths.py --cases eval/cases_20.jsonl
python eval/compare_paths.py
python -m assistant_core --show-sources "I lost my student card"
uvicorn assistant_api.main:create_app --factory
```

Trên máy không có launcher cho Python 3.12, thay `py -3.12` bằng đường dẫn executable Python 3.12. Chạy tại root để tìm `data/` và `eval/`; `LLM_PROVIDER=stub` mặc định không cần mạng. Không commit `.env`, key hay database.

## Giao diện đề xuất để các nhánh độc lập ghép được

- `build_service(settings, fail_provider=False)` dựng cùng service cho CLI/API; nếu `KB_DIR` không khai báo thì tìm `ASSISTANT_DATA_DIR/kb`, không có thư mục KB thì dùng handbook JSON cũ. `KB_DIR`, `RETRIEVAL_KIND` và `RETRIEVAL_MIN_SCORE` có thể đặt qua env; BM25 mặc định 2.0, không dùng nguyên ngưỡng này cho TF-IDF mà không hiệu chỉnh.
- `RagAnswerer(index, llm, min_score, k, prompt_version, retries)` nhận index có `search(query, k)` trả `Hit(chunk, score)`; `llm.complete(prompt)` trả JSON. `llm=None` là retrieval-only; index rỗng cùng answerer là baseline deterministic.
- `Response` và API giữ các trường cũ, thêm `path`, `escalate`, `confidence`; ID JSON cũ dạng `H26-5.3`, ID chunk dạng `H26#5.3`. CLI JSON giữ bốn trường cũ; API trả thêm các trường Lab 06.
- Guard privacy chạy trước router khi có RAG; không đủ nguồn trả `abstain`, `escalate=true`, không gọi model; provider lỗi hoặc JSON/citation sai sau hai lượt sẽ trích top hit và `degraded=true`. Kiểm tra citation chỉ chứng minh ID thuộc tập được cung cấp, không chứng minh nội dung đúng.
- Các thay đổi A1/A2, KB và practice trong nhánh này chỉ là bản cá nhân để review. Huy, Quyền, Minh và Bảo vẫn làm trên nhánh riêng; khi ghép chọn một bản được review, chạy lại bảng và toàn bộ gate trên commit cuối.

Kiểm tra CLI `--list-rules`, `--show-sources`, `--fail-provider`, `--credit-rate`, `--session-id`; kiểm tra API chat, request ID, feedback và restart cùng SQLite bằng `tests/test_lab6_integration.py`. Đừng tạo tag hay nộp LMS trước khi cả nhóm review và xác nhận trạng thái Lab 05.
