# Architecture of `assistant_core`

This document outlines the architectural structure, design principles, and core decisions governing the `assistant_core` service.

---

## 1. Module Overview and Responsibilities

Following the Single Responsibility Principle (High Cohesion, Low Coupling), each module inside `src/assistant_core/` has a distinct, isolated responsibility:

| Module | Responsibility | Public Interface / Exports |
|---|---|---|
| `models.py` | Typed request/response domain models & enums | `Message`, `Response`, `Intent`, `Source`, `Rule` |
| `errors.py` | Domain-specific named exception hierarchy | `AssistantError`, `ConfigError`, `DataError`, `InvalidRequest`, `ProviderError` |
| `config.py` | 12-Factor environment configuration and validation | `Settings`, `load_settings` |
| `knowledge.py` | Data loading and semantic/token lookup for offices and rules | `Office`, `OfficeDirectory`, `Handbook` |
| `tools.py` | Deterministic calculations (tuition & credits parsing) | `parse_credits`, `tuition` |
| `router.py` | Intent classification based on user text | `route`, `GREETINGS` |
| `responder.py` | Explanation generation protocol and offline adapters | `Responder`, `TemplateResponder`, `StubLLMResponder` |
| `service.py` | Central facade & coordinator orchestrating all components | `AssistantService` |
| `logging_setup.py` | Structured JSON logging to `stderr` with secret masking | `JsonFormatter`, `setup_logging` |
| `__main__.py` | CLI entry point supporting single queries & interactive REPL | CLI command execution |

---

## 2. Public Service Interface

The service exposes a unified, single entry point method:

```python
AssistantService.handle(msg: Message) -> Response
```

### Data Contract

- **`Message`**:
  - `text: str`: Cleaned string with length between 1 and 2,000 characters. Reject empty or whitespace-only inputs via Pydantic validator.
  - `session_id: str`: Session identifier (default `"local"`).
- **`Response`**:
  - `answer: str`: Formatted natural language response.
  - `intent: Intent`: Categorized intent (`GREETING`, `FEE`, `OFFICE`, `RULE`, `UNKNOWN`).
  - `sources: list[Source]`: List of supporting source records (`id`, `title`). Each `Response` owns an independent instance (`Field(default_factory=list)`).
  - `degraded: bool`: Boolean flag set to `True` only if an upstream provider failure occurred and a fallback was used.

### Exception and Error Policy

1. **User input errors**: Raise `InvalidRequest` in domain tools or `ValidationError` at models boundary. The service converts `InvalidRequest` on tuition into friendly guidance while maintaining `degraded=False`.
2. **Startup errors**: `ConfigError` (invalid environment variable types/ranges, missing API key when non-stub) and `DataError` (missing CSV/JSON, malformed schema) halt startup immediately with exit code 1.
3. **Upstream provider failures**: Upstream `ProviderError` exceptions are caught within `service._rule()`. The service logs a warning to `stderr`, falls back to `TemplateResponder`, retains the rule source, and marks `degraded=True`. Provider failures never leak raw exceptions to the caller.

---

## 3. Key Architectural Decisions and Rationales

### Decision 1: Pure Functional Deterministic Tuition Calculation (`tools.py`)
- **Decision**: Financial tuition calculation is executed via deterministic pure Python functions (`parse_credits` and `tuition`) rather than using an LLM prompt.
- **Rationale**: Financial calculations require 100% precision, zero hallucination, and reproducible arithmetic. Pure functions have no side effects, no I/O, no dependency on external services, and are trivial to test with parameterized unit tests covering edge cases (e.g. credits 0, out-of-range, negative numbers).

### Decision 2: Pluggable Responder Adapter Protocol (`responder.py`)
- **Decision**: LLM interactions are decoupled behind a `Responder` Protocol. In Week 3, two offline implementations are provided: `TemplateResponder` (deterministic template string) and `StubLLMResponder` (offline stub with configurable failure flag).
- **Rationale**: Adheres to the Dependency Inversion Principle. The core service never interacts with proprietary network APIs directly. Tests and CI run 100% offline, deterministically, without requiring API tokens or incurring network latency. Live LLM providers can be slotted in during future iterations without modifying `AssistantService`.

### Decision 3: 12-Factor App Environment Configuration (`config.py`)
- **Decision**: Configuration is strictly separated from application code using environment variables and optional `.env` loading (`override=False`). Sensitive fields (`llm_api_key`) are configured with `Field(repr=False)`.
- **Rationale**: In accordance with Twelve-Factor App Principle III (Config) and Principle XI (Logs), secrets and runtime parameters are never hard-coded in source files or repository commits. `repr=False` omits the field from model repr only; it does not redact model_dump(), arbitrary logs or tracebacks. The CLI emits only request metadata; subprocess tests check that a synthetic key and full question do not appear in logs.
