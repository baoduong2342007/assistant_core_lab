# Lab 3 — Before / After Maintainability Comparison

**Member:** Phạm Quốc Bảo (`simble2k`)
**Assigned Modules:** Models (`models.py`), Errors (`errors.py`), Responders (`responder.py`), Fallback/contract tests

## 1. Comparison Table

| Question | Before (Monolith) | After (`assistant_core`) |
|---|---|---|
| Where would you change the credit rate? How many places? | 1 constant in code (`RATE = 450000`, line 8) | 1 variable in `.env` (`CREDIT_RATE_VND`) |
| Can you run the tests without internet or an API key? | Yes; simulated provider is offline, but random failure makes printed checks unreliable | Yes (100% offline unit and integration tests with pytest) |
| What happens if `handbook.json` is missing? | Prints `"could not load handbook"` and continues silently | Raises `DataError` at startup with clear path information |
| Is any secret printed or logged? | Yes (`API_KEY` printed in debug output) | CLI log checks verify key/full query absence; repr=False alone is not a redaction guarantee |
| How long does it take a new teammate to find the fee logic? | Fee logic embedded in handle; no human search time measured | Located in tools.py; no human search time measured |
| Number of global variables | 9 (including 3 mutable: `history`, `offices`, `handbook`) | 4 assigned names (version, exports, greetings, logger); no global conversation/data containers |
| Number of bare `except:` blocks | 3 (`load()` x2, `main()` x1) | 0 bare except; broad Exception handlers remain in config/knowledge |
| Lines in the longest function | 56 inclusive lines (`handle()`) | 71 lines (CLI main); service.handle is 32 |
| `ruff check` issues | 8 diagnostics with isolated E,F,I,B,UP,BLE, line120 | 0 diagnostics with the same rule set |
| Can you swap the LLM without touching the service? | No (direct call inside `handle()`) | Yes (`Responder` Protocol decouples implementation) |

## 2. Three Sentences Reflection

1. **What improved most**: Replacing magic return strings and blind exceptions with a structured domain exception hierarchy (`AssistantError`, `ProviderError`, `InvalidRequest`) and typed Pydantic models provides strict contract boundaries and prevents silent failures.
2. **What got more complex**: Defining formal protocols (`Responder`), multiple offline implementations (`TemplateResponder`, `StubLLMResponder`), and independent test fixtures introduces more structural boilerplate up-front compared to a monolithic script.
3. **What you would still change**: I would extend the `Responder` Protocol to support streaming chunks or structured metadata schemas in subsequent labs once asynchronous LLM calls are introduced.

## Measurement correction — 2026-10-25

Dương used Codex to correct factual claims during PR #17 review; this is not a new personal reflection by Bảo. Source hashes and per-module AST counts are in [metrics.json](metrics.json). Function lengths count def through last statement inclusively. Globals count top-level assigned names, excluding imports/classes. Ruff 0.6.9 command: `python -m ruff check --isolated --select E,F,I,B,UP,BLE --line-length 120 reference/monolith/assistant_monolith.py`, then the same command for `src/assistant_core`.

Code smells and responsible modules:

1. Hardcoded configuration/key — Huy, config/logging.
2. Global office/handbook data — Quyền, knowledge loaders.
3. Bare loader exceptions — Quyền, DataError boundaries.
4. Oversized request handler — Dương, service orchestration.
5. Mixed diagnostics and answers — Huy/Dương, logging and CLI.
6. Fee parsing mixed with orchestration — Minh, pure tools.
7. Random/sleep-based provider simulation — Bảo, deterministic responders.
8. Print-only checks — each owner, pytest; Bảo responders and Dương integration.
9. Direct provider coupling — Bảo/Dương, injected Responder protocol.

Validation after branch correction: 107 pytest cases passed, Ruff check/format/BLE passed. Bảo should confirm personal ownership and the original prompt/reflections before claiming individual completion.
