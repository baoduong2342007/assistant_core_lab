# Lab 3 — Monolith Baseline & Code Smell Audit

## 1. Baseline Execution

Command executed:
```bash
python assistant_monolith.py --test
```

### Observed Baseline Outputs:
1. **Greeting**: `"Hello! I can help with offices, fees and rules."`
2. **Tuition**: `18 credits + 2 retake` calculated at `RATE = 450000`, `RETAKE_RATE = 1.5` -> `"Your tuition is 9450000 VND"`
3. **Office lookup**: `"where is the library"` -> `"Library: room B.201, open Mon-Sat 07:00-20:00"`
4. **Rule search**: `"can I register my thesis with 118 credits"` -> Matched rule ID `"H26-5.3"` (Thesis registration), answer printed with `(source: H26-5.3)`.
5. **Too many credits**: `"tuition 40 credits"` -> `"too many credits"`
6. **Empty message**: `""` -> `"empty"`
7. **Random failure**: In approx 10% of calls, `random.random() < 0.1` throws an unhandled exception causing flaky, non-deterministic test results.

---

## 2. Identified Code Smells & Module Mapping

| # | Code Smell in Monolith | Location | Detriment | Responsible Module |
|---|---|---|---|---|
| 1 | Hard-coded secret printed in debug logs | `API_KEY`, `llm()` | Leaks API credentials into logs and git history | `config.py`, `logging_setup.py` |
| 2 | Configuration mixed with application code | `RATE`, `RETAKE_RATE`, `MODEL`, `DEBUG` | Changing rates or providers requires editing source code | `config.py` |
| 3 | Global mutable state | `history`, `offices`, `handbook` | Hidden coupling, concurrency hazards, un-testable | `knowledge.py`, `service.py` |
| 4 | Bare `except:` clauses | `load()`, `main()` | Masks syntax errors, typing mistakes, and `KeyboardInterrupt` | `errors.py`, specific catches |
| 5 | God function doing everything | `handle()` | Violates SRP; mixes routing, regex, arithmetic, search, and LLM calls | `service.py`, `router.py`, `tools.py` |
| 6 | Magic return strings | `"empty"`, `"saved"`, `"too many credits"` | Callers cannot distinguish errors from valid answers | `models.py`, `errors.py` |
| 7 | Unstructured `print()` instead of logging | Throughout monolith | No log levels, unparseable by machines, mixes with stdout answers | `logging_setup.py` |
| 8 | Hand-made tests that only print | `test()` | No assertions, cannot be run automatically in CI | `tests/` with `pytest` |
| 9 | String concatenation for file paths | `BASE + "/data/..."` | Breaks across different operating systems (e.g. Windows vs POSIX) | `pathlib.Path` in `knowledge.py` |
| 10 | Non-deterministic random failure | `random.random() in llm()` | Causes flaky tests; unable to reliably verify logic | `responder.py` (offline stubs) |
