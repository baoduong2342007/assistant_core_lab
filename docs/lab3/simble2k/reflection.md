# Lab 3 — Homework H3: Reading and Reflection

**Author:** Nguyễn Tấn Bảo (`simble2k`)

## 1. Readings Completed
- The Twelve-Factor App: Factors I, II, III, XI.
- Python Packaging User Guide.

## 2. Reflection
The monolith lacked contract boundaries, returning magic strings (`"empty"`, `"saved"`) and swallowing crashes with `except Exception:`. By establishing typed Pydantic request/response structures and named exceptions (`InvalidRequest`, `ProviderError`), callers can cleanly differentiate between valid domain guidance, validation errors, and controlled fallbacks.
