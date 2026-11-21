# Assistant Core Lab — Lab 3 team project

An offline academic-assistant core with greeting, tuition, office lookup and source-bearing handbook answers.
The integrated base was merged in [Minh's PR #1](https://github.com/baoduong2342007/assistant_core_lab/pull/1).
[Dương's PR #16](https://github.com/baoduong2342007/assistant_core_lab/pull/16) adds verified baseline evidence,
integration acceptance coverage, CLI validation fixes and accurate classroom tracking/docs.

## Setup (PowerShell, Python 3.10/3.12)

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\python.exe -m assistant_core "tuition for 18 credits and 2 retake"
.\.venv\Scripts\python.exe -m assistant_core "where is the library"
.\.venv\Scripts\python.exe -m assistant_core "can I register my thesis with 118 credits"
.\.venv\Scripts\python.exe -m assistant_core --fail-provider "can I register my thesis with 118 credits"
```

Run from the repository root so default data/ resolves, or set ASSISTANT_DATA_DIR to an absolute path.
No .env or API key is needed for stub mode. Optional .env loading does not override existing environment.
Run with no query for interactive mode; quit/EOF exits. Answers go to stdout, JSON logs to stderr.
Expected startup/request errors exit 1; invalid argparse usage exits 2. Service fee-validation guidance
is a normal fee response. Existing --json/--log-level/--credit-rate flags came with PR #1; their presence
alone does not complete anyone's H1 assignment.

## Quality checks

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m ruff format --check .
.\.venv\Scripts\python.exe -m ruff check --select BLE .
```

Current suite: 90 cases. CI validates Python 3.10/3.12, builds and imports the installed wheel outside checkout.
This is not a claim that every requirement or all team submissions are complete.

## Materials, boundaries and evidence

- Original starter and worksheets: reference/, pinned source and SHA-256 manifest in reference/manifest.json.
- Runtime data: data/, identical sample lab data; not a statement of current university regulations.
- Actual baseline: docs/lab3/baseline.md and baseline-evidence.json. Upstream fake-key debug output is redacted
  in recorded evidence; original source is unchanged.
- Interface/module map and three decisions: docs/architecture.md; concrete contracts: docs/contracts.md.
- Roles/review guidance: docs/team.md; owner issues: docs/tracking.md.
- Honest submission status and remaining gaps: docs/submissions/week3.md.

Scope: greeting/fee/office/rule/unknown and controlled provider fallback; no real AI calls, FastAPI/UI,
history/stats/save migration, or claim of finished H1/H2/H3 work. Remaining owner fixes are tracked in
docs/lab3/open-items.md. The existing v0.3-core tag predates completed release verification; leave it intact
and do not treat its existence alone as successful release evidence.

### Session context for logs (Huy H1 draft)

Use `python -m assistant_core --session-id run-42 --json "hi"` to correlate handled events.
The ID is also used for every request in an interactive run; the default is `local`.
IDs are 1–64 ASCII letters/digits with optional `_`/`-`, starting with a letter/digit.
Use an opaque ID rather than a name, query or credential. Invalid IDs exit 2 before startup.
Answers/JSON remain on stdout; log metadata remains on stderr. Existing `--log-level` precedence is preserved.
This feature is a distinct H1 proposal because `--log-level` was already in the integrated base.

### Displaying rule sources in plain text

`python -m assistant_core --show-sources H26-5.3` displays the answer followed by
source IDs and titles. It also works in interactive mode and with provider fallback.
Responses without sources do not show a source section. `--json` already includes
sources and cannot be combined with `--show-sources`.

## Lab04 — bài cá nhân Trần Quốc Huy

Cài bằng `python -m pip install -r requirements.txt` và `python -m pip install -e .`.
Từ root repo, sao chép `.env.example` thành `.env`, đặt `API_ADMIN_KEY` cho local rồi chạy:

```bash
uvicorn assistant_api.main:create_app --factory --reload
```

Mở `http://127.0.0.1:8000/docs`; giữ `LLM_PROVIDER=stub` để chat không cần API key.
Chạy `python -m pytest -q`, `python -m pytest -q practice/` và `bash api-tests/curl_tests.sh`.
Terminal curl phải đặt `API_ADMIN_KEY` giống server; script không đọc `.env` và chỉ in status,
nên cần đối chiếu từng kết quả. Đọc [contract](docs/lab4/api_contract.md),
[bàn giao Huy](docs/lab4/tqhuy0602/status.md) và [cấu hình/weather](docs/lab4/tqhuy0602/weather-checks.md).


## List loaded handbook rules

Run `python -m assistant_core --list-rules` to list titles in handbook order. Add `--show-sources` for IDs or `--json` for structured output. An empty handbook has an explicit result. Listing does not call the provider or search, and cannot be combined with a query.

### Lab 5 persistence

The API stores chat metadata and feedback in SQLite at `sqlite:///assistant.db` by default. Set `DATABASE_URL` to choose the file and `SESSION_SALT` to a private, stable value in your local `.env`; the built-in salt is only suitable for local exercises. Keep the same salt across restarts to group the same session consistently. Raw messages and raw session IDs are not stored; feedback comments are stored. A valid chat request ID is required when submitting feedback. Admin authentication is required for feedback listing and `/v1/stats`.

### Lab 6 — Huy: settings, LLM adapter và A2

Chạy tại root với `LLM_PROVIDER=stub` để dùng offline; `template` dùng retrieval không gọi model.
`ollama` dùng `LLM_MODEL` và `LLM_BASE_URL` (mặc định `http://localhost:11434`);
`openai` yêu cầu `LLM_API_KEY`, model tương thích và base URL mặc định `https://api.openai.com/v1`.
`LLM_TIMEOUT_S` phải dương; `RETRIEVAL_KIND=bm25` mặc định có `RETRIEVAL_MIN_SCORE=2.0`.
Prompt được đóng gói trong wheel; JSON/schema/citation sai hoặc provider lỗi sau hai lượt sẽ fallback về đoạn nguồn.
Xem [hồ sơ bàn giao Huy](docs/lab6/tqhuy0602/status.md) và [bảng 20/25 câu](docs/lab6/tqhuy0602/path_comparison.md).

## Lab 7 — Streamlit UI và HTTP client của Huy

Từ root repo, dùng Python 3.10 hoặc 3.12 (local đã kiểm Python 3.11.16):

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip install -e .
```

Streamlit được ghim `1.39.0`. Cả hai terminal dưới đây chạy tại root và dùng cùng venv.

```bash
# Terminal 1: FastAPI, offline stub, SQLite demo riêng
source .venv/bin/activate
export LLM_PROVIDER=stub
export DATABASE_URL=sqlite:///assistant_lab7_demo.db
python -m uvicorn assistant_api.main:create_app --factory --host 127.0.0.1 --port 8000
```

```bash
# Terminal 2: UI chỉ gọi backend bằng HTTP
source .venv/bin/activate
export ASSISTANT_API_URL=http://127.0.0.1:8000
python -m streamlit run ui/app.py
```

PowerShell dùng `. .\.venv\Scripts\Activate.ps1` để kích hoạt venv;
đặt `$env:LLM_PROVIDER = 'stub'` và `$env:DATABASE_URL = 'sqlite:///assistant_lab7_demo.db'` ở terminal API;
đặt `$env:ASSISTANT_API_URL = 'http://127.0.0.1:8000'` ở terminal UI, rồi chạy cùng hai lệnh `python -m ...` phía trên.
Mở [UI](http://localhost:8501) và [OpenAPI](http://127.0.0.1:8000/docs).

`ASSISTANT_API_URL` phải đặt trong **terminal chạy Streamlit**, không phải chỉ trong terminal FastAPI hoặc file `.env` của backend.
Nếu bỏ biến này, UI dùng `http://127.0.0.1:8000`; URL chỉ nhận HTTP/HTTPS, không nhận credentials/query/fragment.
Client mặc định chờ tối đa 20 giây mỗi thao tác HTTP và 2 giây khi kiểm health.
Timeout, 422, 429, lỗi server và lỗi mạng có thông báo cùng bước xử lý; lỗi feedback giữ nút để thử lại, chỉ xác nhận và ẩn nút sau HTTP 201.

Chạy warm-up riêng trong `practice/`, dừng nó trước khi mở chat vì cùng dùng cổng 8501:

```bash
cd practice
python -m streamlit run hello_streamlit.py
# Ở terminal khác, cùng thư mục practice:
python -m pytest -q test_hello_streamlit.py
```

Test chính tại root tự thu thập `tests/test_ui.py` cùng test client/AppTest bổ sung:

```bash
python -m pytest -q
python -m pytest -q tests/test_ui.py tests/test_lab7_huy_client.py tests/test_lab7_huy_app.py
python -m ruff check .
python -m ruff format --check .
```

Hồ sơ, ảnh desktop/375 px, D.4 và trạng thái H1/H2 ở [bàn giao Lab 7 của Huy](docs/lab7/tqhuy0602/status.md).
