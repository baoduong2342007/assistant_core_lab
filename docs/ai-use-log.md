# AI Use Disclosure Log

In accordance with course guidelines and the Git & GitHub tutorial (Chapter 18.11), all AI assistant interactions used for scaffolding, refactoring, and code analysis are recorded below.

## Log Entries

| Date | Member | Purpose | Tool Used | Prompts & Actions | Human Verification & Modifications |
|---|---|---|---|---|---|
| 2026-10-24 | All Members | Monolith smell identification | Antigravity AI | Analyzed `assistant_monolith.py` for anti-patterns | Verified all 10 code smells against Twelve-Factor and Clean Code principles |
| 2026-10-24 | Dương (`baoduong2342007`) | Packaging and Service Skeleton | Antigravity AI | Scaffolding `pyproject.toml`, `AssistantService` | Added `session_id`, strict dependency injection, CLI JSON export |
| 2026-10-24 | Huy (`tqhuy0602`) | Configuration and JSON Logging | Antigravity AI | Scaffolding Pydantic `Settings`, `JsonFormatter` | Implemented `repr=False` on `llm_api_key`, handler deduplication, log level validation |
| 2026-10-24 | Quyền (`pqquyenn`) | Knowledge Loaders | Antigravity AI | Office CSV & Handbook JSON parser classes | Wrapped file/schema errors in `DataError`, implemented case-insensitive matching |
| 2026-10-24 | Minh (`luongnhatinh`) | Deterministic Tools & CI Workflow | Antigravity AI | Parsing regex for credits, GitHub Actions YAML | Added negative number rejection, matrix testing across Python 3.10 and 3.12 |
| 2026-10-24 | Bảo (`simble2k`) | Domain Models & Error Hierarchy | Antigravity AI | Pydantic models and Exception classes | Added `Field(default_factory=list)` to avoid mutable default sharing, whitespace rejection |
