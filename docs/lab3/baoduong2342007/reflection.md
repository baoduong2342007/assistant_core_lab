# Lab 3 — Homework H3: Reading and Reflection

**Author:** Bảo Dương (`baoduong2342007`)

## 1. Readings Completed
- The Twelve-Factor App: Factors I, II, III, and XI.
- Python Packaging User Guide: Packaging Python Projects.

## 2. Reflection
The monolith script committed the fundamental flaw of treating application code, runtime data, environmental configuration, and secrets as a single tangled blob. By structuring `assistant_core` into a formal Python package with `pyproject.toml`, standard `src/` layout, pinned dependencies, and 12-Factor config/log stream handling, we transformed an unmaintainable personal script into a production-grade, collaborative service. Modularization allowed each team member to own an independent, testable module with clean interfaces and zero merge conflicts.
