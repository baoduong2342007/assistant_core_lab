# Lab 3 — Before / After Maintainability Comparison

**Member:** Trần Quang Huy (`tqhuy0602`)  
**Assigned Modules:** Config (`src/assistant_core/config.py`), `.env.example`, Logging (`src/assistant_core/logging_setup.py`)

## 1. Comparison Table

| Question | Before (Monolith) | After (`assistant_core`) |
|---|---|---|
| Where would you change the credit rate? How many places? | 1 constant in code (`RATE = 450000`, line 8) | 1 variable in `.env` (`CREDIT_RATE_VND`) |
| Can you run the tests without internet or an API key? | No (10% random crash simulation, no automated test harness) | Yes (100% offline unit and integration tests with pytest) |
| What happens if `handbook.json` is missing? | Prints `"could not load handbook"` and continues silently | Raises `DataError` at startup with clear path information |
| Is any secret printed or logged? | Yes (`API_KEY` printed in debug output) | No (`repr=False` masks key, structured logging to stderr) |
| How long does it take a new teammate to find the fee logic? | Had to parse messy branching inside 65-line `handle()` | Immediate lookup in `src/assistant_core/tools.py` |
| Number of global variables | 9 (including 3 mutable: `history`, `offices`, `handbook`) | 0 (all state passed via dependency injection) |
| Number of bare `except:` blocks | 3 (`load()` x2, `main()` x1) | 0 (all catches specify concrete domain or standard exceptions) |
| Lines in the longest function | ~65 lines (`handle()`) | ~25 lines (`AssistantService.handle()`) |
| `ruff check` issues | 19 issues (E401, I001, E722, E711, BLE001, E501) | 0 issues across all rules (E, F, I, B, UP, BLE) |
| Can you swap the LLM without touching the service? | No (direct call inside `handle()`) | Yes (`Responder` Protocol decouples implementation) |

## 2. Three Sentences Reflection

1. **What improved most**: Configuration and logging are completely separated from code; secrets are protected using `repr=False`, and logs are emitted as structured JSON on `stderr`.
2. **What got more complex**: Validating types and environment defaults with Pydantic adds schema code.
3. **What you would still change**: I would add support for file-based rotating log handlers for production deployments.
