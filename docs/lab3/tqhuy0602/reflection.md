# Lab 3 — Homework H3: Reading and Reflection

**Author:** Trần Quang Huy (`tqhuy0602`)

## 1. Readings Completed
- The Twelve-Factor App: Factors I, II, III (Config), and XI (Logs).
- Python Packaging User Guide.

## 2. Reflection
The monolith violated Factor XI (Logs) by abusing `print()` statements for debugging, mixing operational logs with user outputs on stdout, and dumping API keys. By introducing a structured JSON formatter writing strictly to stderr and masking secrets with `repr=False`, our logging is now machine-parseable, observable, and safe.
