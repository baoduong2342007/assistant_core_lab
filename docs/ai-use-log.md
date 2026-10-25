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
