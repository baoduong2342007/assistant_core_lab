# Lab 3 — Homework H3: Reading and Reflection

**Author:** Nguyễn Tấn Bảo (`simble2k`)  
**Assigned Modules:** Models, Named Errors, Responders, Test Harness

---

## 1. Twelve-Factor App Analysis

### Factor I: Codebase (One codebase tracked in revision control, many deploys)
The starter monolith was a single-file script without repository boundaries, version tags, or separation between reference data and runtime state. In `assistant_core_lab`, we separated reference materials (`reference/monolith/`) from source code (`src/assistant_core/`), established a git branching strategy with automated continuous integration, and prepared tagged releases (`v0.3-core`).

### Factor II: Dependencies (Explicitly declare and isolate dependencies)
The monolith relied implicitly on global interpreter environments and undeclared dependencies. In contrast, our refactored architecture declares strict version ranges in `pyproject.toml` (`pydantic>=2.7,<3`, `python-dotenv>=1.0,<2`), pins lockfiles in `requirements.txt`, and uses editable development builds (`pip install -e .`) within an isolated virtual environment.

### Factor III: Config (Store config in the environment)
The original script hardcoded critical financial and system constants directly into source code (`RATE = 450000`) and leaked sensitive credentials during debugging. Our team externalized configuration into environment variables (`CREDIT_RATE_VND`, `LLM_PROVIDER`, `LOG_LEVEL`), provided a safe `.env.example`, and added startup validation through dedicated configuration models.

### Factor XI: Logs (Treat logs as event streams)
The monolith abused `print()` for debugging, diagnostic output, and user responses interchangeably, interleaving sensitive information with standard stdout. The new design routes business answers strictly to stdout and formats structured JSON log events directly to stderr, omitting raw payloads and credentials.

---

## 2. Python Packaging and Layout

Adopting the modern `src/` layout prevents accidental import of uninstalled local directories and forces standard packaging practices. Using `pyproject.toml` with `setuptools.build_meta` standardizes metadata, specifies required Python versions (`>=3.10`), and cleanly defines public module exports in `__init__.py`.

---

## 3. Reflection on Domain Models, Errors, and Modularity

### Violations in the Monolith
The most egregious maintainability violation in the monolith was its complete lack of domain contracts:
1. **Magic Strings**: States and failure modes were communicated using arbitrary strings like `"empty"` or `"saved"`.
2. **Blind Exception Swallowing**: Bare `except:` clauses obscured critical failures (such as syntax errors or missing files), rendering system debugging nearly impossible.
3. **Coupled Providers**: The LLM interaction was tightly bound inside business logic, causing random 10% crashes and precluding automated testing.

### Architectural Solution
By introducing:
- **Pydantic Models (`models.py`)**: `Message` validates input bounds (1–2000 characters, non-whitespace), while `Response` provides immutable contract fields and isolated `Source` lists.
- **Exception Hierarchy (`errors.py`)**: `AssistantError` serves as the root class for `ConfigError`, `DataError`, `InvalidRequest`, and `ProviderError`, enabling granular catch blocks and clean caller boundaries.
- **Responder Protocol (`responder.py`)**: The runtime `@runtime_checkable` `Responder` protocol decouples caller logic from generation implementations, allowing deterministic offline `TemplateResponder` and testable `StubLLMResponder` to run without network or nondeterminism.

### Cost vs. Benefit of Modularization
While establishing protocols, domain models, and dedicated test fixtures demands higher initial boilerplate than writing a 50-line script, the maintainability return is immediate: 100% offline automated testability, strict contract safety, zero leaked exceptions, and the ability for 5 team members to develop and test components concurrently without merge conflicts.
