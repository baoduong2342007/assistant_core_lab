# Lab 3 — Before / After Maintainability Comparison (Master Index)

This document provides the collective comparison between the original `assistant_monolith.py` and the refactored `assistant_core` package, along with links to each team member's worksheet.

## Comparison Summary

| Metric / Question | Monolith (`assistant_monolith.py`) | Refactored (`assistant_core`) |
|---|---|---|
| Where would you change the credit rate? How many places? | 1 constant hardcoded in code (`RATE = 450000`) | 1 environment variable in `.env` (`CREDIT_RATE_VND`) |
| Can you run the tests without internet or an API key? | No (simulated provider flakes randomly; no real tests) | Yes (100% offline, deterministic stubs and unit tests) |
| What happens if `handbook.json` is missing? | Prints error and silently continues with broken search | Raises explicit `DataError` at startup, exits with code 1 |
| Is any secret printed or logged? | Yes (`API_KEY` printed in debug prompt) | No (masked with `repr=False`, structured JSON logging) |
| How long does it take a new teammate to find the fee logic? | Needs to read through 163-line script to find `handle()` | Instantly located in dedicated `src/assistant_core/tools.py` |
| Number of module-level global variables | 9 (including 3 mutable globals: `history`, `offices`, `handbook`) | 0 (pure dependency injection) |
| Number of bare `except:` blocks | 3 | 0 (specific exception handling, BLE001 clean) |
| Lines in the longest function | ~65 lines (`handle()`) | ~25 lines (`AssistantService.handle()`) |
| `ruff check` issues | 19 issues (E401, I001, E722, E711, BLE001, E501) | 0 issues (clean pass across all rules) |
| Can you swap the LLM without touching the service? | No (tightly coupled within `handle()`) | Yes (decoupled via `Responder` Protocol) |

---

## Individual Member Worksheets

- [Lương Nhật Minh (`luongnhatinh`)](luongnhatinh/before_after.md)
- [Bảo Dương (`baoduong2342007`)](baoduong2342007/before_after.md)
- [Trần Quang Huy (`tqhuy0602`)](tqhuy0602/before_after.md)
- [Phan Quốc Quyền (`pqquyenn`)](pqquyenn/before_after.md)
- [Nguyễn Tấn Bảo (`simble2k`)](simble2k/before_after.md)
