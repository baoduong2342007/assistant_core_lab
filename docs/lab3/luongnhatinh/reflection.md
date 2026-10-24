# Lab 3 — Homework H3: Reading and Reflection

**Author:** Lương Nhật Minh (`luongnhatinh`)

## 1. Readings Completed
- The Twelve-Factor App:
  - Factor I: **One codebase tracked in revision control, many deploys**
  - Factor II: **Explicitly declare and isolate dependencies**
  - Factor III: **Store config in the environment**
  - Factor XI: **Treat logs as event streams**
- Python Packaging User Guide: *Packaging Python Projects* (`pyproject.toml`, build backends, `src/` layout).

---

## 2. Reflection

### Which factor did the monolith violate most egregiously?
The monolith violated **Factor III (Config)** and **Factor II (Dependencies)** most egregiously. In `assistant_monolith.py`, database-like configurations (tuition rate `RATE = 450000`, multiplier `RETAKE_RATE = 1.5`), environment toggles (`DEBUG = True`), and secret credentials (`API_KEY = "sk-test-2b7c1d9e4f0a"`) were hard-coded directly into the script. This meant that deploying the code to a different environment or changing business parameters required editing the source code itself, creating huge risks of leaking credentials into Git history and logs.

### How did our refactoring address this?
In our refactored architecture:
1. All configuration is consolidated into a typed Pydantic `Settings` class in `src/assistant_core/config.py`.
2. Settings are populated from environment variables using `python-dotenv` with `override=False`, prioritizing system environment variables over `.env`.
3. Secret keys use `Field(repr=False)` so they are never printed in console dumps, debug logs, or error stack traces.
4. An `.env.example` file is provided as a committed template, while `.env` is explicitly ignored by Git in `.gitignore`.

### Was the architectural cost of modularization worth it?
Yes, absolutely. While breaking down a 160-line script into 10 modules introduced more files and abstractions, it established clear boundaries of responsibility. Testing individual components (such as testing tuition calculations without loading the handbook, or testing handbook search without a network connection) became trivial. Furthermore, having clear module boundaries allowed a team of 5 people to work concurrently on separate pull requests without stepping on each other's code.
