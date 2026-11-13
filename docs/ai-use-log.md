# AI Use Disclosure Log

In accordance with course guidelines and the Git & GitHub tutorial (Chapter 18.11), all AI assistant interactions used for scaffolding, refactoring, and code analysis are recorded below.

## Log Entries

| Date | Member | Purpose | Tool Used | Prompts & Actions | Human Verification & Modifications |
|---|---|---|---|---|---|
| 2026-10-24 | Shared entry imported from PR #1; individual use unconfirmed | Monolith smell identification | Antigravity AI (reported in PR #1) | Analyzed `assistant_monolith.py` for anti-patterns | Each member confirms their own use; Dương used Codex as recorded below |
| 2026-10-24 | Dương (`baoduong2342007`) | Foundation and classroom integration (PR #16) | Codex | Source/baseline verification, integration, CLI validation, tests and docs | 19 added acceptance cases; 90 tests and clean-clone checks passed; runtime base credited to PR #1 |
| 2026-10-24 | Huy (`tqhuy0602`) | Configuration and JSON Logging | Antigravity AI | Scaffolding Pydantic `Settings`, `JsonFormatter` | Implemented `repr=False` on `llm_api_key`, handler deduplication, log level validation |
| 2026-10-24 | Quyền (`pqquyenn`) | Knowledge Loaders | Antigravity AI | Office CSV & Handbook JSON parser classes | Wrapped file/schema errors in `DataError`, implemented case-insensitive matching |
| 2026-10-24 | Minh (`luongnhatinh`) | Deterministic Tools & CI Workflow | Antigravity AI | Parsing regex for credits, GitHub Actions YAML | Added negative number rejection, matrix testing across Python 3.10 and 3.12 |
| 2026-10-24 | Bảo (`simble2k`) | Domain Models & Error Hierarchy | Antigravity AI | Pydantic models and Exception classes | Added `Field(default_factory=list)` to avoid mutable default sharing, whitespace rejection |
| 2026-11-01 | Minh (`luongnhatinh`) | Lab 04 REST API, CI, H1 & Reflection | Antigravity AI | Scaffolding FastAPI routes, Pydantic schemas, sorting offices, unit tests | Verified with pytest, curl script, Swagger /docs, and manual code inspection |

## PR #1 required-check repair — 2026-10-24

Dương used Codex to diagnose missing Foundation check contexts, copy the reviewed foundation workflow, and preserve Ruff default exclusions. Local validation: 71 pytest tests passed; Ruff check/format/BLE and sdist/wheel build passed. Runtime implementation and other members' reports were left unchanged. This is a CI repair, not a complete runtime code review.


2026-10-24 — Bảo used AI assistance to explore the initial implementation of exact rule ID lookup (H1). The AI drafted a naive loop raising a generic Exception on miss. Bảo conducted a code review, rejected the generic exception in favor of returning None, added whitespace and case normalization, implemented guard clauses against empty inputs, and verified behavior with 8 unit and fallback integration tests in `tests/test_h1_rule_by_id.py`. Full review documented in `docs/lab3/simble2k/ai_extension_review.md`.

## Dương — PR #16 classroom integration (2026-10-24)

Codex, at Dương's request, verified pinned starter files, ran the unchanged baseline, measured AST/Ruff
metrics, prepared tracking/docs and integrated the main branch. It fixed validation of existing CLI
overrides and added 19 real acceptance cases (90 total). Initial core/service/CLI implementation came
from PR #1 and is not claimed as Dương's original implementation. No personal reports for others were
written in this work. Earlier table entries are retained from PR1 and require each person's verification.
Review/merge, instructor acceptance of the shared-module workflow, and team release remain separate gates.

## Dương — merge closeout (2026-10-25)

Codex assisted the issue/status audit and review of PR #17. PR #16 was approved by simble2k and merged as a2ad759. Dương contributed CLI validation fixes, 19 acceptance cases, source/baseline measurements, packaging verification and integration documentation. Main validation: 90 pytest cases passed. Other members' AI tools remain their own disclosures.

## PR #17 branch correction — 2026-10-25

At Dương's request, Codex merged main and the AI-disclosure closeout branch into simble2k's branch, preserving both histories. Dương/Codex wired exact ID lookup into the production service, replaced duplicate test-only implementations with real service/CLI tests, and corrected factual worksheet metrics with source hashes. Local result: 107 tests passed; Ruff check/format/BLE passed. Original responder/fixture commits remain credited to simble2k; these fixes are Dương's Codex-assisted contribution. No new personal reflection or independent human verification by Bảo is claimed.
## Trần Quốc Huy — config/logging owner follow-up (2026-10-25)

Người phụ trách code: **Trần Quốc Huy (`tqhuy0602`)**. **Codex hỗ trợ toàn bộ**: đọc plan và code nền,
đề xuất và trực tiếp chỉnh implementation/tests, chạy kiểm tra, đo AST/Ruff, sửa tên tác giả,
soạn worksheet/reflection nháp và chuẩn bị branch/PR. Code/tests/docs do AI tạo được giữ lại.
Không xác nhận các claim Antigravity/"human verification" trong bảng cũ; đó là dữ liệu nhận từ PR1.

Thay đổi thực tế: giới hạn provider stub/template; validate multiplier hữu hạn và các miền số;
bỏ broad catch config, thông báo lỗi không chứa giá trị environment; loại key khỏi model serialization;
quản lý handler JSON theo stream stderr hiện tại. Tests: 113 passed trên Python 3.11, Ruff check/BLE đạt;
worksheet ghi số đo thật trong `docs/lab3/tqhuy0602/metrics.json`. Peer review, CI đúng SHA,
đọc H3 cá nhân và nộp LMS được theo dõi riêng, không tự đánh dấu hoàn thành.

## Trần Quốc Huy — H1 session ID proposal (2026-10-25)

Code owner: **Trần Quốc Huy**. **Codex hỗ trợ toàn bộ**, including the retained initial proposal,
implementation, assisted review/three real improvements, 16 new cases and the report.
The existing --log-level flag is not claimed as new. Validation: 129 pytest passed, Ruff check/format passed
on macOS/Python 3.11.16. Initial proposal/report live under docs/lab3/tqhuy0602.
Draft depends on core PR19/HOME-01; no human approval, H1 merge or personal reading is asserted.


## Minh classroom correction — 2026-10-26

Dương requested Codex to fix Minh's remaining classroom items. Codex changed pure credit parsing and
integer validation, added 25 tests, measured/corrected Minh's worksheet and code-smell mapping, and
prepared issue/PR tracking. Original implementation and reflections remain attributed to Minh/PR1;
these follow-up edits are not claimed as Minh's personal actions. H1/H2/H3 are outside this correction.


## Quyền classroom correction — 2026-10-26

Dương asked Codex to fix Quyền's remaining classroom work and merge PR24 after validation. Codex wrote
CSV/JSON validation and concrete exception handling, 37 regression cases, measured worksheet corrections
and issue/PR evidence. Existing runtime authorship and original reflections remain attributed to PR1/Quyền;
these fixes and measurements are not described as Quyền's personal manual work. No reading/hours or
H1/H2/H3 completion is invented.


## Dương classroom coordination/index closeout — 2026-10-26

At Dương's request, Codex verified live merged PRs, issue states, main checks and collaborator access,
prepared the five-member classroom submission/worksheet index and corrected stale tracking. Runtime
code and personal worksheets/reflections are unchanged in this documentation-only task. The source
commit, test provenance and dated API snapshot are linked in docs/submissions/week3.md. Huy/Bảo personal
confirmations, peer review, final issue #10 closure and LMS submission are not fabricated.

## Dương H1 follow-up — 2026-10-27

At Dương's request Codex implemented `--show-sources` after finding that the planned
`--json` feature already existed in the core. It displays the IDs and titles returned
by the service in plain text, supports interactive mode and fallback, and rejects a
redundant combination with `--json`. Tests cover those cases and source-free answers.
Codex wrote the implementation, tests, and this disclosure; Dương's independent
review, a preserved initial proposal with three documented review improvements,
peer review, and a merged H1 PR remain outstanding. No claim of personal completion
is made by this entry.

## Quyền H1 draft — 2026-10-30

At the user’s request Codex implemented and tested the `--list-rules` feature, added documentation and flagged unverified claims in the existing report. Quyền’s independent review, three evidenced improvements, personal confirmation and peer review remain pending.


## Phan Quỳnh Quyền — Lab04 REST API, Offices H1 & Part F Rate Limiting (2026-11-02)

Người thực hiện: **Phan Quỳnh Quyền (pqquyenn)**. Hỗ trợ bởi **Antigravity AI**:
- Hỗ trợ triển khai bài thực hành Warm-up P1–P5 (practice/hello_api.py, practice/test_hello_api.py).
- Xây dựng tầng HTTP API src/assistant_api/ kết nối với AssistantService của core Lab 3:
  - POST /v1/chat (T1) hỗ trợ validation chuỗi trắng, trả đầy đủ trường ChatResponse.
  - POST /v1/feedback (T2) và GET /v1/feedback (T3) bảo vệ bởi admin key.
  - GET /v1/weather (T4) với kiểm thực cấu trúc upstream và fallback cache cũ stale=True.
- Hoàn thiện bài tập H1 chuyên trách: thêm OfficeDirectory.all() trong src/assistant_core/knowledge.py, endpoint GET /v1/offices trả danh sách văn phòng sắp xếp theo thứ tự bảng chữ cái và kiểm thử 2 test case theo yêu cầu.
- Bật Part F rate limiting bắt buộc theo IP client bằng RateLimiter và RATE_LIMIT_PER_MIN.
- Kiểm thử độc lập: toàn bộ 240 tests trong 	ests/ và 5 tests warm-up đều pass; kiểm tra lint/format Ruff 100% đạt chuẩn; chạy kiểm chứng curl thực tế lưu tại docs/lab4/pqquyenn/curl_tests.log.


## Minh H1 feature — 2026-10-30

Minh implemented the `--credit-rate` CLI override option allowing users to override `settings.credit_rate_vnd` for single runs and interactive sessions. AI coding assistant (Antigravity AI) was used to scaffold CLI arguments and initial proposals. Minh manually audited the code and made three concrete improvements: kept `tuition()` pure by passing overrides via `Settings` at the CLI boundary, rejected non-positive credit rates with non-zero exits, and preserved session isolation. Dedicated test suite added in `tests/test_h1_credit_rate.py`. Report documented in `docs/lab3/luongnhatinh/ai_extension_review.md`.




## Trần Quốc Huy — nộp H2 qua GitHub PR #41 (02/11/2026)

Huy yêu cầu nộp bài và chọn rõ “Nộp qua PR #41 trên GitHub”. Codex giữ nội dung H2
hiện tại đúng 5 dòng, cập nhật hồ sơ/PR để gửi review, giữ ghi nhận AI hỗ trợ.
Đây là chỉ định nộp bản hiện tại; không khẳng định Huy tự viết, đã tự đọc/diễn đạt lại,
đã có peer approval hoặc đã nộp LMS.





## Trần Quốc Huy — Lab04 (01/11/2026)

Theo yêu cầu “Làm phần của Trần Quốc Huy”, Codex đọc PLAN_TUAN4 và main thực tế,
dùng scaffold/học liệu chính thức tại a848a96, triển khai P1–P5, T1–T4, H1 cá nhân,
Settings/env/admin auth và các test config/weather bằng MockTransport/clock giả.
Codex hỗ trợ toàn bộ code, tests, contract, bản nháp reflection, Git và minh chứng curl/Swagger;
các phần AI tạo được giữ lại và disclose. Core nhóm tuần 3 và fixtures chung được bảo toàn.

Kết quả local Python 3.11.16: 274 passed, 1 skipped bonus; practice 5 passed;
Ruff lint/format/BLE đạt; curl thật và POST chat qua Swagger trả đúng status.
Chưa nhận Huy tự viết/đọc reflection, tự review hoặc đã nộp LMS.
Chi tiết và các mục cần xác nhận ở `docs/lab4/tqhuy0602/status.md`.

In accordance with course guidelines and the Git & GitHub tutorial (Chapter 18.11), all AI assistant interactions used for scaffolding, refactoring, and code analysis are recorded below.





## 2026-11-03 — Dương-requested correction of Huy PR41

At Dương's request, Codex enabled Part F for chat, removed the Lab04 rate-limit
skip, and restored the Week 3 tests/test_config.py byte-for-byte. API configuration
cases and their environment fixture now live in tests/test_api_config.py.
RateLimiter uses a lock for concurrent chat handlers. These corrections are
AI-assisted, not claimed as Huy's independent manual work.






## Bảo (`simble2k`) — Lab 04 REST API, Schemas & Feedback (2026-11-01)

Code owner: **Phạm Quốc Bảo (`simble2k`)**. Antigravity AI hỗ trợ triển khai cấu trúc schemas, validation (đặc biệt là lọc chuỗi toàn khoảng trắng cho `POST /v1/chat` và ràng buộc rating cho feedback), endpoints T1–T4, H1 `OfficeDirectory.all()`, bộ fixtures kiểm thử độc lập trong `tests/test_api.py`, tài liệu `docs/lab4/api_contract.md` và dàn ý reflection.
Bảo đã trực tiếp kiểm tra mã nguồn, chạy kiểm thử cục bộ (`pytest -q`, `ruff check`, `ruff format`), xác minh kết quả curl script và đối chiếu Swagger UI.

On 2026-11-02, following updated homework guidance designating Part F rate limiting as required for team submission, Antigravity AI assisted in implementing thread-safe rate limiting on `POST /v1/chat`, unskipping unit test coverage, adding client isolation and sliding window expiry tests, and handling upstream malformed weather JSON payloads without modifying Week 3 tests. Bảo verified all 231 pytest unit tests, Ruff lint and format checks locally.

On 2026-11-02 (follow-up review P2 fix), following peer review by Dương (`baoduong2342007`) on PR #39, Antigravity AI assisted in preventing non-finite numbers (NaN, Infinity, -Infinity) from entering the weather cache by configuring `Field(allow_inf_nan=False)` on `Weather` schema and adding explicit `math.isfinite()` validation in `WeatherClient.current()`. Non-finite values are caught, triggering upstream retries, falling back to stale cache if present (HTTP 200 stale), or raising `ExternalServiceError` (HTTP 503) without crashing serialization (HTTP 500). Added regression tests for both cached and non-cached scenarios (236 passed, 0 skipped).







## 2026-11-03 — Dương-requested correction of Bảo PR39

At Dương's request, Codex validated all required upstream fields before caching,
including time/weather_code, and added 18 Lab04 regressions for invalid payloads
with/without a stale cache. Missing metadata now follows retry/503 or stale-cache
fallback. This correction is AI-assisted; no independent manual work is claimed.
Existing Week 3 tests are unchanged.








## Dương — Lab04 API (2026-11-01)

At Dương's request, Codex adapted the public Lab04 starter and warm-up, wired the
existing Lab03 core into FastAPI, implemented chat, feedback, weather and offices,
added tests, extended CI and wrote the API contract. Source: CSC10014
public_materials commit a848a96d44876d4baee5eabe645114cf56d0b82f. Local checks:
223 passed and 1 optional skip before the added settings test; the focused API and
practice run passed 17 tests with 1 optional skip. Ruff checks passed; the curl log
is in docs/lab4/curl-results.txt. GitHub CI passed on Python 3.10 and 3.12. Dương
must review and explain the work and write the required personal reflection. No
human review, hours, LMS submission or group approval are claimed.

Codex also captured the Swagger chat screenshot and wrote the five-line reflection in docs/lab4/baoduong2342007/reflection.md; it is AI-written and Dương should review and personalize it before submission.

On 2026-11-01, after Dương supplied the updated homework instruction requiring Part F, Codex enabled the chat rate limit and updated Lab04 tests and documentation. Existing Week 3 tests were not modified.









## 2026-11-02 — Dương weather correction and assisted review

Codex validated the upstream weather structure and finite numeric values before caching, added 14 regression cases in a new Lab04 test file, and ran the full suite: 240 passed; practice: 5 passed; Ruff lint/format passed. Week 3 tests were not edited. Codex also inspected PR39 head e253d54 and ran focused API/practice checks (24 passed), finding a remaining non-finite-temperature serialization failure; see docs/lab4/baoduong2342007/review-bao.md. No human approval or LMS submission is asserted.










## 2026-11-03 — Dương-requested correction of Minh PR35

At Dương's request, Codex validated the upstream weather payload before caching,
including finite temperature and wind values, and added 14 Lab04 regression cases
for 503 and stale-cache fallback. This assisted correction is not attributed as
Minh's independent manual work. Existing Week 3 tests are unchanged.









## 2026-11-03 — Dương requested remaining repository closeout

Codex synchronized PR31 with the integrated Lab04 main, retained --list-rules and its tests, corrected the false frozen-Rule claim, and rewrote Dương’s H1 report around the actual --show-sources feature. Reports describe assisted implementation and do not invent owner reading or independent AI review. LMS submission is handled by Dương.

## 2026-11-10 — Bảo (`simble2k`) Lab 05 Persistence & Database Implementation

Phạm Quốc Bảo used Antigravity AI to plan and scaffold the Lab 05 database persistence layer according to `PLAN_TUAN5.md`.
Implemented `src/assistant_api/db.py` (SQLModel models `ChatSession`, `Interaction`, `Feedback`, helper methods, and `Repository` with R1 `add_feedback` and R2 `list_feedback`).
Created unit tests in `tests/test_lab5_db.py` and restart persistence verification in `tests/test_lab5_persistence.py`.
Configured `sqlmodel>=0.0.22` in `pyproject.toml` and `requirements.txt`.
Verified all 331 pytest test cases, Ruff lint/formatting, SQL practice answers (15/15), and school repository tests (5/5).
Conducted peer review for Minh's PR (`docs/lab5/simble2k/review-minh.md`) and compiled H3 schema analysis in `docs/lab5/simble2k/status.md`.

