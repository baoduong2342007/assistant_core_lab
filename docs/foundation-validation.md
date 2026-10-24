# Foundation validation — 2026-10-24

Local environment: Windows, Python 3.13. Python 3.10/3.12 are validated by the PR's Foundation matrix;
local 3.13 checks do not substitute for that matrix.

Executed successfully:

- `python -m pip install -r requirements.txt` and `python -m pip install -e .`.
- `python -c "import assistant_core; print(assistant_core.__file__)"` resolves to this checkout's src package.
- `python -m ruff check .`, `python -m ruff format --check .`, `python -m ruff check --select BLE .`.
- `python -m build` produced sdist and wheel.
- Unchanged reference comparison, runtime data equality and four baseline assertions;
  20 additional print-based starter runs (see lab3/baseline-evidence.json).

Project Ruff exclusion now extends defaults so `.git` and virtual environments remain excluded;
the original `exclude = ["reference"]` replaced those defaults.
Pytest is scoped to tests/ to avoid collecting the intentionally flawed reference monolith.
There are no behavioral tests or implemented models/errors yet, so no pytest-pass claim is made.
CI explicitly reports that state and runs real editable/wheel import checks instead.

The wheel check uses a clean virtual environment and an import outside the checkout. It validates the
distribution only; it is not a fresh-clone verification of a completed runtime core or a release gate.
Use the final PR check links for exact commits and Python 3.10/3.12 results.
