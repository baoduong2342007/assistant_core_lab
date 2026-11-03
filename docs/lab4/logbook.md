# Lab04 logbook — Dương

## 2026-11-01

- Codex implemented P1–P5, T1–T4 and H1 on branch `feat/lab04-baoduong2342007`; [draft PR #36](https://github.com/baoduong2342007/assistant_core_lab/pull/36).
- Verified core/API locally: 223 passed, 1 optional skip before adding a settings test; the subsequent focused API/practice run passed 17, skipped 1. Curl responses are recorded in `curl-results.txt`. GitHub CI passed on Python 3.10 and 3.12.
- [Python bootcamp W3 tag](https://github.com/baoduong2342007/python-bootcamp/releases/tag/py-w3-done) was pushed at Dương's request. The tag does not establish peer review or independent teammate verification.
- Swagger `/docs` returned 200 for chat; the screenshot is `swagger-chat.png`. Codex prepared the five-line reflection at `baoduong2342007/reflection.md`; AI assistance is disclosed and Dương should review it before submission.
- Pending: Dương’s review of the reflection, peer review, LMS submission, group integration and Lab04 tag. Actual human hours and peer contributions have not been provided.

## Updated homework requirement

Dương supplied an instruction requiring Part F rate limiting. Codex enabled the limiter on chat, unskipped the Lab04 rate-limit test and added client-isolation and expiry coverage. Existing Week 3 tests remain unchanged.

## 2026-11-02 — Dương weather correction and assisted review

Codex validated the upstream weather structure and finite numeric values before caching, added 14 regression cases in a new Lab04 test file, and ran the full suite: 240 passed; practice: 5 passed; Ruff lint/format passed. Week 3 tests were not edited. Codex also inspected PR39 head e253d54 and ran focused API/practice checks (24 passed), finding a remaining non-finite-temperature serialization failure; see docs/lab4/baoduong2342007/review-bao.md. No human approval or LMS submission is asserted.


## Huy branch coordination notes

# Lab04 logbook — phần Trần Quốc Huy

| Ngày | Người phụ trách | Công việc thực tế | Bằng chứng | Còn lại |
|---|---|---|---|---|
| 01/11/2026 | Trần Quốc Huy, Codex hỗ trợ toàn bộ | P1–P5, T1–T4, H1; Settings/admin/weather; test và tài liệu | [Status](tqhuy0602/status.md), [weather checks](tqhuy0602/weather-checks.md), [curl](tqhuy0602/curl-results.txt), [Swagger](tqhuy0602/swagger-chat.png) | Huy tự xác nhận/diễn đạt H2 và nộp LMS; peer review; nhóm chọn candidate |
| 01/11/2026 | Codex hỗ trợ Huy | Rà PR36 ở commit 2a4f269, tái hiện lỗi upstream JSON sai cấu trúc trả 500 | [Nhận xét có bằng chứng](tqhuy0602/review-duong.md) | Huy đọc, quyết định gửi nhận xét; chưa nhận là human review/approval |
| 02/11/2026 | Trần Quốc Huy yêu cầu, Codex thực hiện | Chọn bản H2 hiện tại để nộp qua PR #41, giữ AI-use disclosure | [H2](tqhuy0602/reflection.md), [PR #41](https://github.com/baoduong2342007/assistant_core_lab/pull/41) | Peer review và quy trình tích hợp nhóm; chưa nộp LMS |

Giờ công cá nhân: chưa được Huy cung cấp, không dùng thời gian chạy AI để tự điền.
H2 do Codex hỗ trợ, đúng 5 dòng; Huy yêu cầu nộp bản hiện tại qua PR #41 ngày 02/11/2026.
Không ghi thay đóng góp, review hay xác nhận của các thành viên khác.
