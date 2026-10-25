# CL-01 baseline — observed 2026-10-24

Executed unchanged pinned starter with Python 3.13.14 from `reference/monolith/`.
Full commands, exit codes and outputs: [baseline-evidence.json](baseline-evidence.json).
The fake key printed by upstream debug output is redacted in that evidence only.

| Input | Observed |
| --- | --- |
| hi | Hello! I can help with offices, fees and rules. |
| tuition for 18 credits and 2 retake | Your tuition is 9450000 VND |
| where is the library | Library: room B.201, open Mon-Sat 07:00-20:00 |
| can I register my thesis with 118 credits | Answer includes source H26-5.3 |

All four standalone commands exited 0. Twenty additional `--test` executions exited 0;
0 of those executions printed `LLM timeout` and returned the source-bearing fallback.
The starter's print-based test has no assertions; exit 0 alone is not a test-suite pass.
Random failures are an upstream behavior; the future stub must be deterministic.

AST measurements: 9 module-level assigned names, 3 bare except handlers,
longest function `handle` = 56 lines (definition through final statement, inclusive).
Ruff 0.6.9 reported 8 diagnostics with E,F,I,B,UP,BLE and line length 120, isolated from project exclusion.
Core behavior, fallback, validation and CLI acceptance tests remain pending implementation.
