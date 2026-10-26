# Minh — classroom tools/router/CI worksheet

Assigned owner: luongnhatinh. Original implementation: merged PR #1.
This correction is performed by Dương with Codex on 2026-10-26 at the user's request.
It records actual code measurements and fixes; it does not claim Minh personally performed these edits.

## 1. Before / after comparison

| Question | Before monolith | Current integrated core |
| --- | --- | --- |
| Change credit rate / locations | RATE in one code assignment | CREDIT_RATE_VND in environment; tools receives the rate explicitly, no settings I/O |
| Tests offline / no API key | Yes: fake provider is local; manual tests only print and may fallback randomly | Yes: deterministic offline pytest suite, 171 cases in this validation |
| Missing handbook | Prints warning and continues with existing global state | DataError at startup; missing-data acceptance tests; malformed short CSV rows remain Quyền follow-up |
| Secret logging | Upstream llm prints a fake key/prompt | CLI tests check synthetic key/full question absence; repr=False alone is not universal redaction |
| Locate fee logic | Fee logic inside handle; no human lookup timing measured | tools.py holds parsing/math; router supplies intent; no human timing measured |
| Module-level assigned names | 9 | 4 assigned names; constants/exports/logger included, not zero globals |
| Bare except handlers | 3 | 0 across src; distinguish bare handlers from broad Exception catches in knowledge |
| Longest function | handle: 56 inclusive lines | src/assistant_core/__main__.py::main: 71 lines; service.handle: 32 |
| Ruff diagnostics | 8 with Ruff0.6.9 isolated E,F,I,B,UP,BLE / line120 | 0 project diagnostics with same rules; reference excluded from project gates |
| Swap responder without service edits | handle calls llm directly | Responder injection and source-preserving ProviderError fallback |

Definitions, file hashes and per-module measurements: [metrics.json](metrics.json).

## 2. Three reflections retained from PR #1

These are the existing report's statements, retained rather than inventing personal reflections.
Minh should review/confirm them and be able to explain the corrected parser.

1. **What improved most**: The fee calculation logic is now completely isolated into pure, deterministic functions (`parse_credits`, `tuition`) that can be tested across all boundary conditions without spinning up runtime state.
2. **What got more complex**: Creating separate files and type definitions adds initial boilerplate compared to a single flat script.
3. **What you would still change**: I would enhance the credit parser to support natural language phrasing like "twelve credits" in addition to digits.

## 3. Code smells and responsible parts

1. Hard-coded configuration/key — Huy config/logging.
2. Mutable global history/knowledge — Quyền loaders and Dương injection.
3. Bare except handlers — module owners' domain errors, Dương CLI.
4. Oversized handle — Dương orchestration and owner modules.
5. Fee parsing/math mixed with I/O — Minh pure tools.
6. Repeated routing logic — Minh shared router; stats excluded from core.
7. Print diagnostics mixed with answer — Huy logging and Dương CLI streams.
8. String paths / file lifecycle — Quyền Path/context managers.
9. Random failure/sleep — Bảo deterministic responders.
10. Print-only tests — each owner assertions; Minh boundaries/priority and Dương integration.

## 4. Actual classroom correction and validation

Numeric expressions such as 18.5 credits, 1.5 retake, .5, fractions/grouped numbers and scientific
notation are rejected before digit extraction. Negative counts stay invalid. Retake digits are removed
by their source span, not by matching a number's value. Pure tuition also rejects fractional/bool counts.
Added 25 regression/acceptance cases covering these paths, valid queries, inclusive 1/30 boundaries,
fee-before-office routing and service guidance with degraded=False instead of a wrong monetary result.

Windows/Python 3.13.14: 171 pytest passed; Ruff check/format/BLE passed. CI 3.10/3.12 is verified on
the actual follow-up PR head. No homework extension/reading/completion claim is added here.
