# Phan Quỳnh Quyền — classroom knowledge worksheet

Owner: pqquyenn. PR: https://github.com/baoduong2342007/assistant_core_lab/pull/24
Core knowledge implementation came from PR1. Quyền's initial PR24 standardized the name and recorded
verification. Dương subsequently requested Codex to fix loader validation, add real coverage and correct
this worksheet. These corrections are not claimed as Quyền's personal manual actions.

## 1. Before / after (10 rows)

| Question | Before monolith | Current integrated core |
| --- | --- | --- |
| Change credit rate / locations | RATE in one code assignment | One CREDIT_RATE_VND setting; pure tuition receives rate |
| Tests offline without a key | Yes: upstream fake provider is local, random fallback and print-only checks | Yes: 208 assertion-based offline tests, no real API credential |
| Missing / corrupt handbook | Bare except prints warning and continues with global data | DataError for missing/invalid JSON/schema/UTF-8; CLI startup exits1 on invalid data |
| Secret logging | Upstream fake key and prompt printed by llm | CLI regressions check synthetic key/full query absence; repr=False alone is not universal redaction |
| Find fee logic | Inside handle; no human lookup time measured | Dedicated tools.py; no human lookup time measured |
| Module-level assigned names | 9 | 4 assigned names, including package exports/version/logger/constants; no global conversation/data containers |
| Bare except handlers | 3 | 0 in src; knowledge now catches expected I/O/decoding/parser errors only |
| Longest function | handle: 56 inclusive lines | src/assistant_core/__main__.py::main: 71 lines; service.handle: 32 |
| Ruff diagnostics | 8 with Ruff0.6.9 isolated E,F,I,B,UP,BLE / line120 | 0 project diagnostics; original reference source deliberately excluded |
| Swap responder without service edits | handle directly calls llm | Shared Responder protocol/injection; sources preserved on controlled fallback |

Actual definitions, source hashes and per-module AST metrics: [metrics.json](metrics.json).

## 2. Three reflections retained from the original owner report

The following statements are retained as the original report, not newly invented personal reflections.
Quyền should read/confirm them and explain the loader changes.

1. **What improved most**: Loading office directory and handbook data is now cleanly isolated into `OfficeDirectory` and `Handbook` with strong validation that raises `DataError` on missing or corrupt files.
2. **What got more complex**: Creating custom dataclasses and models requires more structure than loading raw JSON dictionaries.
3. **What you would still change**: I would add BM25 or embedding-based vector search in a future iteration to improve retrieval precision beyond keyword overlap.

## 3. Code smells / responsible modules

1. Hard-coded configuration/key — Huy config/logging.
2. Mutable global offices/handbook — Quyền one-time loaders, Dương injection.
3. Bare loader exceptions — Quyền concrete expected errors and DataError.
4. Oversized handle — Dương orchestration, delegated owner modules.
5. File path concatenation — Quyền pathlib.Path.
6. File lifecycle leaks — Quyền context-managed UTF-8 reads.
7. Mixed print diagnostics/answers — Huy logging and Dương CLI streams.
8. Random/sleep-based provider — Bảo deterministic responders.
9. Print-only manual tests — owner assertions; Quyền fixtures/error/tie tests.
10. Parsing/calculation mixed with routing — Minh pure tools/router.

## 4. Actual correction and validation

CSV validates every required cell before strip(), rejects missing/blank/extra cells, and reports path/line.
Strict CSV parsing and specific OSError/UnicodeError/csv.Error catches map expected failures to DataError.
JSON requires non-empty strings for id/title/text instead of coercing null/numbers/containers to strings;
schema errors identify the file and record. No new business algorithm or homework extension is added.

Added 37 tests: malformed CSV/encoding, wrong JSON container/record/field types and missing fields,
stable ties/no match, file-order office selection, loaded data surviving removal of source files, and
two CLI subprocess regressions for malformed data producing exit1 without a traceback.
Windows/Python3.13.14: 208 pytest passed; Ruff check/format/BLE passed. CI validates Python3.10/3.12.
