# Lab 3 — AI Extension Review

**Author:** Trần Quang Huy (`tqhuy0602`)  
**Feature:** CLI runtime log level override (`--log-level`)

---

## 1. Prompt Used
```text
Add a --log-level option to the assistant_core CLI to allow overriding the log level for this run (DEBUG, INFO, WARNING, ERROR).
```

---

## 2. Code Review and Three Concrete Improvements

| # | What the AI Generated | Problem Found | What I Changed | Why |
|---|---|---|---|---|
| 1 | `logging.basicConfig(level=args.log_level)` directly in CLI. | Did not use our structured `JsonFormatter` and reset configured handlers. | Routed log level change through `Settings` and called `setup_logging(level)`. | Maintains uniform JSON logging formatting on stderr. |
| 2 | Added duplicate handlers every time `setup_logging()` was called. | Repeated logs in test runs and multiple messages per event. | Added check in `setup_logging()` to prevent duplicate StreamHandlers on stderr. | Ensures idempotent logging setup. |
| 3 | Accepted invalid log levels like `--log-level RANDOM` which crashed logging. | Crashed at runtime with unhandled `ValueError`. | Added Pydantic validator on `Settings.log_level` checking against valid Python log level names. | Guarantees fail-fast configuration error handling. |

---

## 3. Checklist Verification

- [x] **Interfaces respected**: Integrates with `Settings` and `logging_setup.py`.
- [x] **No secrets leaked**: Masked in `Settings(repr=False)`.
- [x] **Tests added**: Verified in `tests/test_config.py` and `tests/test_logging.py`.
