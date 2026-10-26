# Assistant Core Lab — Lab 3 team project

An offline academic-assistant core with greeting, tuition, office lookup and source-bearing handbook answers.
The integrated base was merged in [Minh's PR #1](https://github.com/baoduong2342007/assistant_core_lab/pull/1).
[Dương's PR #16](https://github.com/baoduong2342007/assistant_core_lab/pull/16) adds verified baseline evidence,
integration acceptance coverage, CLI validation fixes and accurate classroom tracking/docs.

## Setup (PowerShell, Python 3.10/3.12)

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\python.exe -m assistant_core "tuition for 18 credits and 2 retake"
.\.venv\Scripts\python.exe -m assistant_core "where is the library"
.\.venv\Scripts\python.exe -m assistant_core "can I register my thesis with 118 credits"
.\.venv\Scripts\python.exe -m assistant_core --fail-provider "can I register my thesis with 118 credits"
```

Run from the repository root so default data/ resolves, or set ASSISTANT_DATA_DIR to an absolute path.
No .env or API key is needed for stub mode. Optional .env loading does not override existing environment.
Run with no query for interactive mode; quit/EOF exits. Answers go to stdout, JSON logs to stderr.
Expected startup/request errors exit 1; invalid argparse usage exits 2. Service fee-validation guidance
is a normal fee response. Existing --json/--log-level/--credit-rate flags came with PR #1; their presence
alone does not complete anyone's H1 assignment.

## Quality checks

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m ruff format --check .
.\.venv\Scripts\python.exe -m ruff check --select BLE .
```

Current suite: 90 cases. CI validates Python 3.10/3.12, builds and imports the installed wheel outside checkout.
This is not a claim that every requirement or all team submissions are complete.

## Materials, boundaries and evidence

- Original starter and worksheets: reference/, pinned source and SHA-256 manifest in reference/manifest.json.
- Runtime data: data/, identical sample lab data; not a statement of current university regulations.
- Actual baseline: docs/lab3/baseline.md and baseline-evidence.json. Upstream fake-key debug output is redacted
  in recorded evidence; original source is unchanged.
- Interface/module map and three decisions: docs/architecture.md; concrete contracts: docs/contracts.md.
- Roles/review guidance: docs/team.md; owner issues: docs/tracking.md.
- Honest submission status and remaining gaps: docs/submissions/week3.md.

Scope: greeting/fee/office/rule/unknown and controlled provider fallback; no real AI calls, FastAPI/UI,
history/stats/save migration, or claim of finished H1/H2/H3 work. Remaining owner fixes are tracked in
docs/lab3/open-items.md. The existing v0.3-core tag predates completed release verification; leave it intact
and do not treat its existence alone as successful release evidence.

### Session context for logs (Huy H1 draft)

Use `python -m assistant_core --session-id run-42 --json "hi"` to correlate handled events.
The ID is also used for every request in an interactive run; the default is `local`.
IDs are 1–64 ASCII letters/digits with optional `_`/`-`, starting with a letter/digit.
Use an opaque ID rather than a name, query or credential. Invalid IDs exit 2 before startup.
Answers/JSON remain on stdout; log metadata remains on stderr. Existing `--log-level` precedence is preserved.
This feature is a distinct H1 proposal because `--log-level` was already in the integrated base.
