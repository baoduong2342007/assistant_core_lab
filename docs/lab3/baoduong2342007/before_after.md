# Dương — classroom integration worksheet

Owner: baoduong2342007. Refactor/integration PR: https://github.com/baoduong2342007/assistant_core_lab/pull/16

The original core, including service/CLI, was introduced by Minh's PR #1, not separately authored by Dương.
Dương's PR verifies/integrates that base, fixes CLI override validation, adds acceptance tests and prepares
packaging, source evidence, tracking and documentation. It does not claim authorship of others' modules.
Initial baseline was captured before these integration changes; see ../baseline-evidence.json.

## Before / after (10 rows)

| Question | Before monolith | Current integrated core |
| --- | --- | --- |
| Change credit rate / locations | RATE in one code assignment | One CREDIT_RATE_VND environment setting; Settings passes rate to pure tuition tool |
| Offline tests without a key | Yes: fake provider is local; manual tests print results and can randomly fallback | Yes: 90 assertion-based pytest cases, deterministic responder; no real key needed |
| Missing handbook | load catches broadly, prints warning, continues with global handbook | DataError at startup, stderr message, exit 1; subprocess missing-data case covered |
| Secrets printed or logged | llm prints upstream fake key and part of prompt | CLI acceptance checks fake env key and full query absent from logs; repr=False alone is not a general redaction guarantee |
| New teammate finds fee logic | Mixed into handle; no human timing measured | tools.py is linked from architecture; no human timing measured |
| Module-level assigned names | 9 | 4: package version/exports, service logger and router greeting vocabulary; no module-level mutable conversation/data containers |
| Bare except handlers | 3 | 0 across src/assistant_core; broad except Exception still exists in config/knowledge and is tracked separately |
| Longest function | handle: 56 inclusive lines | src/assistant_core/__main__.py::main: 71 lines; service.handle: 32 lines |
| Ruff diagnostics | 8 with Ruff0.6.9 E,F,I,B,UP,BLE / line120 / --isolated | 0 project diagnostics with those rules; reference deliberately excluded |
| Swap responder without changing service | handle directly calls llm | Constructor-injected Responder; controlled ProviderError uses template with source/degraded preserved |

Measurement definition and per-module results: [metrics.json](metrics.json). Global-name counts include
constants/logger names, not imports/classes; distinguish these from mutable domain state.

## Code smells and owners

1. Hard-coded config/key: Huy settings and logging.
2. Mutable global history/offices/handbook: Quyền loaders; Dương constructor injection.
3. Bare except in loaders/input: Quyền domain errors; Dương explicit CLI handling.
4. Oversized handle: Dương service delegates to owners' modules.
5. Business print mixed with logs: Huy JSON logging; Dương stdout/stderr separation.
6. Fee parsing/math mixed with orchestration: Minh pure tools.
7. String paths and unclosed JSON file: Quyền Path/context managers.
8. Random failure and sleep: Bảo deterministic stub.
9. Print-only tests: each owner assertions; Dương subprocess acceptance.
10. Repeated routing in stats: Minh route; history/stats intentionally outside core scope.

## Three reflections

The largest improvement is the injected service boundary, which lets CLI tests cover real wiring while
service tests exercise fallback and validation independently.
Configuration and dependency wiring add complexity, and the CLI remains the longest function; the numbers
above describe that tradeoff rather than claiming every function became shorter.
Next I would coordinate the remaining parser/config/knowledge fixes with their owners before a core release.
