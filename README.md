# Assistant Core Lab — team foundation

Lab 3 team repository. Current branch prepares CL-00/CL-01 and packaging/documentation for CL-02.
Only an importable `assistant_core` package skeleton exists here. Runtime models, config, knowledge,
tools/router, responders, service and CLI are pending owner PRs. There are no business tests yet.

## Setup (PowerShell, Python 3.10 or 3.12)

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\python.exe -c "import assistant_core; print(assistant_core.__file__)"
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m ruff format --check .
```

`python -m assistant_core` is not available until Dương's later service/CLI PR.
Pinned development/runtime dependencies are in requirements.txt; metadata uses compatible ranges.

## Unchanged baseline

```powershell
cd reference/monolith
..\..\.venv\Scripts\python.exe assistant_monolith.py --test
```

Starter debug output intentionally prints a fake key and prompt; do not copy this into core.
Data is sample lab data, not current university policy. Source verification: reference/manifest.json.
Observed baseline and raw evidence: docs/lab3/baseline.md.

## Working together

Roles/reviewers: docs/team.md. Proposed contracts: docs/contracts.md (review pending).
After foundation and Bảo's models/errors merge, branch from updated main for each owner's module.
Include issue link, actual validation, worksheet and AI disclosure in each PR; peer review before merge.
The five-person module split differs from the tutorial's individual-refactor flow; disclose and confirm it.

PR #1 scope/integration findings: docs/lab3/pr1-review.md. Its CI and existing v0.3-core tag do not mean
this skeleton is a completed runtime release. H1/H3 and other members' reports are outside this branch.
