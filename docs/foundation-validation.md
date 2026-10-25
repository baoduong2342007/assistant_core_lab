# Dương classroom integration validation — 2026-10-24

Windows, Python 3.13.14. Python 3.10/3.12 validation is the PR CI matrix, not this local runtime.

Executed checks for the integrated branch:

- Pinned requirements and editable install/import passed.
- `python -m pytest -q`: 90 passed, including 19 new CLI/service acceptance cases.
- Ruff 0.6.9 check, format --check and BLE passed.
- Original reference manifest hashes and runtime/reference data equality passed.
- Baseline: four actual commands/assertions and 20 unchanged --test runs (no timeout observed).
- CLI cases cover invalid overrides, startup failures, whitespace/oversized input, argparse exit2,
  EOF/quit/blank lines/recovery, source/degraded on rule success/failure, unknown and log metadata/privacy.
- Service cases verify invalid fee guidance keeps fee intent and only ProviderError becomes fallback.

Measured counts: lab3/baoduong2342007/metrics.json. Starter outputs: lab3/baseline-evidence.json.
No business test-pass claim is inferred from the starter's print-only --test.

A clean-clone report alongside this document records the exact tested commit, environment, commands
and outputs. A later documentation-only commit may record that report.
Final team/release acceptance still depends on owner items in lab3/open-items.md.
