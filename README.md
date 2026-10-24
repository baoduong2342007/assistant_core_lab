# Assistant Core Lab (`assistant_core`)

[![CI](https://github.com/baoduong2342007/assistant_core_lab/actions/workflows/ci.yml/badge.svg)](https://github.com/baoduong2342007/assistant_core_lab/actions)

Computational Thinking — Lab 3: Maintainable Python Service (Team 03 repository).

A modular, testable, and maintainable Python service refactored from an unmaintainable monolith script into a clean 12-Factor service architecture.

---

## Architecture Overview

```text
       ┌──────────┐
       │   CLI    │
       │ __main__ │
       └────┬─────┘
            │ calls
            ▼
    ┌────────────────┐
    │AssistantService│◄─────────┐
    │   service.py   │          │
    └───────┬────────┘          │
            │                   │
   ┌────────┼────────┬──────────┼──────────┐
   ▼        ▼        ▼          ▼          ▼
router    tools   knowledge  responder   config
 Intent  tuition   offices   Stub/Templ   .env
                  handbook
```

- **Single Service Interface**: Every caller (CLI, future FastAPI in Lab 4, and UI in Lab 7) enters via `AssistantService.handle(msg: Message) -> Response`.
- **Pure Functional Tools**: Deterministic tuition calculation isolated in `tools.py`.
- **Pluggable Responder Adapter**: `Responder` Protocol with `TemplateResponder` and `StubLLMResponder` runs 100% offline and deterministic.
- **12-Factor Configuration & Logging**: Pydantic `Settings` reading from environment / `.env`; structured single-line JSON logging to `stderr`.

---

## Getting Started

### 1. Clone and Create Virtual Environment
```bash
git clone https://github.com/baoduong2342007/assistant_core_lab.git
cd assistant_core_lab
python -m venv .venv

# On Linux / macOS:
source .venv/bin/activate
# On Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
pip install -e .
```

### 3. Configure Environment
```bash
cp .env.example .env
```

---

## Running the Assistant CLI

Run single queries:
```bash
python -m assistant_core "tuition for 18 credits and 2 retake"
python -m assistant_core "where is the library"
python -m assistant_core "can I register my thesis with 118 credits"
```

Output formatted as JSON (via `--json`):
```bash
python -m assistant_core --json "where is the library"
```

Simulate upstream provider failure with fallback:
```bash
python -m assistant_core --fail-provider "can I register my thesis with 118 credits"
```

Interactive mode:
```bash
python -m assistant_core
```

Separate logs (`stderr`) from answers (`stdout`):
```bash
python -m assistant_core "hi" 2> app.log
```

---

## Quality Gates & Testing

Run all quality checks:
```bash
# 1. Pytest suite (71 passing tests)
pytest -q

# 2. Ruff lint check
ruff check .

# 3. Ruff format check
ruff format --check .

# 4. Ruff blind exception check
ruff check --select BLE .
```

---

## Project Structure

```text
assistant_core_lab/
├── .github/workflows/ci.yml       # GitHub Actions CI workflow
├── pyproject.toml                 # Package metadata and build config
├── requirements.txt               # Pinned dependencies
├── .env.example                   # Environment configuration template
├── .gitignore
├── README.md
├── data/                          # Runtime data (offices.csv, handbook.json)
├── reference/                     # Untouched starter materials & monolith
├── src/assistant_core/
│   ├── __init__.py                # Package exports
│   ├── __main__.py                # CLI entry point
│   ├── config.py                  # Pydantic Settings & environment loader
│   ├── errors.py                  # Domain exception hierarchy
│   ├── knowledge.py               # OfficeDirectory and Handbook search
│   ├── logging_setup.py           # Structured JSON logging to stderr
│   ├── models.py                  # Message, Response, Intent, Rule, Source
│   ├── responder.py               # Responder protocol, Template and Stub
│   ├── router.py                  # Intent classification
│   ├── service.py                 # Central AssistantService coordinator
│   └── tools.py                   # Pure tuition calculation tools
├── tests/                         # Comprehensive pytest test suite (71 tests)
└── docs/
    ├── architecture.md            # Architecture notes & 3 key decisions
    ├── contracts.md               # Interface contracts
    ├── team.md                    # Team roles and review loop
    ├── ai-use-log.md              # AI disclosure log
    ├── submissions/week3.md       # Submission summary
    └── lab3/                      # Baseline, before/after, and AI reviews
```

---

## Team & Roles

- **Bảo Dương** (`baoduong2342007`): Tech Lead, Packaging, Service, CLI, Release
- **Trần Quang Huy** (`tqhuy0602`): Config, Logging, Tests
- **Phan Quốc Quyền** (`pqquyenn`): Knowledge (Offices, Handbook), Tests
- **Lương Nhật Minh** (`luongnhatinh`): Tools, Router, Ruff, CI
- **Nguyễn Tấn Bảo** (`simble2k`): Models, Errors, Responders, Fallback tests
