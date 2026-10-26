# Lab 3 — Homework H3: Reading and Reflection

**Author:** Phan Quỳnh Quyền (`pqquyenn`)

## 1. Readings Completed
- The Twelve-Factor App: Factors I, II, III, XI.
- Python Packaging User Guide.

## 2. Reflection
In the monolith, `load()` used bare `try: ... except:` and string path concatenation `BASE + "/data/..."` which easily failed across OS environments. In `assistant_core`, using `pathlib.Path` and explicit `DataError` exceptions guarantees robust cross-platform execution and clear error messages when files are missing.
