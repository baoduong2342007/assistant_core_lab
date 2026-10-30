# Lab 3 — AI Extension Review

**Author:** Lương Nhật Minh (`luongnhatinh`)  
**Feature:** Add CLI flag `--credit-rate` to override the tuition rate (VND) for a specific run without editing code or `.env`.

---

## 1. Prompt Used
```text
Extend the assistant_core CLI to support a --credit-rate option that lets the user override the credit rate for this run, passing it to the tuition calculation.
```

---

## 2. Code Review and Three Concrete Improvements

| # | What the AI Generated | Problem Found | What I Changed | Why |
|---|---|---|---|---|
| 1 | Modified `tools.tuition()` to read `os.getenv("CREDIT_RATE")` directly. | Broke purity of `tuition()` function by introducing hidden environmental I/O coupling. | Kept `tuition()` as a pure function; passed rate through `Settings` instance in `__main__.py` to `AssistantService`. | Preserves single responsibility and testability of mathematical tools. |
| 2 | Allowed zero or negative values for `--credit-rate` (e.g. `--credit-rate -50000`). | Negative rates cause negative tuition calculations without error. | Added validation in CLI and `Settings`: rejected non-positive rates with exit code 1. | Guarantees domain validity and prevents erroneous financial computations. |
| 3 | Ignored interaction with `settings.credit_rate_vnd` default when flag is omitted. | The generated code overwrote global state and failed when running in interactive mode. | Attached overridden rate to the local `Settings` object only for the current CLI session. | Isolates runtime configuration without side effects across test runs or sessions. |

---

## 3. Checklist Verification

- [x] **Interfaces respected**: CLI calls `service.handle()`, which delegates to pure `tuition()`.
- [x] **No new unwanted dependencies**: Uses standard `argparse` and existing `Settings`.
- [x] **No secrets leaked**: Masked in `Settings(repr=False)`.
- [x] **No user data logged**: Only operational metadata logged to `stderr`.
- [x] **Tests added**: Dedicated test suite in `tests/test_h1_credit_rate.py` (6 passed) covering rate calculation, JSON export, default rate preservation, rejection of non-positive rates, argument type errors, and interactive mode.
