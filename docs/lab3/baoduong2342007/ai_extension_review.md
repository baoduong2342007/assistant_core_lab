# Lab 3 — AI Extension Review

**Author:** Bảo Dương (`baoduong2342007`)  
**Feature:** CLI structured JSON output flag (`--json`)

---

## 1. Prompt Used
```text
Add a --json option to the assistant_core CLI that outputs the full Response model in valid JSON format to stdout while preserving stderr logging.
```

---

## 2. Code Review and Three Concrete Improvements

| # | What the AI Generated | Problem Found | What I Changed | Why |
|---|---|---|---|---|
| 1 | Used `print(response.__dict__)`. | Produced non-JSON-compliant output (e.g. `{'answer': ...}`) and failed to serialize `Intent` Enum and `Source` objects. | Used `json.dumps()` with explicit serialization of `response.intent.value` and `s.model_dump()`. | Ensures standards-compliant JSON parseable by CLI consumers like `jq`. |
| 2 | Redirected logging records into `stdout` when `--json` was active. | Mixed structured log JSON with the payload JSON, breaking JSON parsers reading `stdout`. | Kept structured logs strictly on `stderr` via `sys.stderr` in `setup_logging()`. | Preserves Unix philosophy: payload on stdout, diagnostics on stderr. |
| 3 | Did not handle errors or empty inputs under `--json`. | Crashed with an unhandled exception traceback on empty messages. | Handled errors gracefully, outputting error messages to stderr with non-zero exit codes. | Provides reliable exit status codes for automation scripts. |

---

## 3. Checklist Verification

- [x] **Interfaces respected**: CLI calls `service.handle(Message) -> Response`.
- [x] **No new unwanted dependencies**: Uses standard library `json` and `argparse`.
- [x] **Tests added**: Comprehensive subprocess CLI test in `tests/test_cli.py`.
