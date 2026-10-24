# Team Organization — Team 03

Lab 3: Maintainable Python Service (`assistant_core_lab`)

## Team Members and Module Ownership

| Member | GitHub Username | Role & Module Responsibilities | Reviewer |
|---|---|---|---|
| **Dương** | `baoduong2342007` | Tech Lead, Skeleton, Packaging, Service, CLI, Architecture, Release | Huy (`tqhuy0602`) |
| **Huy** | `tqhuy0602` | Config (`config.py`), `.env.example`, Logging (`logging_setup.py`), Config tests | Quyền (`pqquyenn`) |
| **Quyền** | `pqquyenn` | Knowledge (`knowledge.py`: CSV/JSON loader, office directory, handbook search), Knowledge tests | Minh (`luongnhatinh`) |
| **Minh** | `luongnhatinh` | Tools (`tools.py`: credit parser, tuition math), Router (`router.py`), Ruff linting, CI workflow | Bảo (`simble2k`) |
| **Bảo** | `simble2k` | Models (`models.py`), Errors (`errors.py`), Responders (`responder.py`), Fallback/contract tests | Dương (`baoduong2342007`) |

## Review & Collaboration Rules

1. **Review Loop**: 5-member peer review rotation: Dương → Huy → Quyền → Minh → Bảo → Dương.
2. **Branching Convention**: `refactor/assistant-core-<username>` branched from `main`.
3. **Quality Gates**: Every PR must pass `pytest -q`, `ruff check .`, `ruff format --check .`, and `ruff check --select BLE .` prior to approval and merge.
