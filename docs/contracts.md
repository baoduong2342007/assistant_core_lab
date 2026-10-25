# Contracts and Module Boundaries

## Public Interface Contract

```python
AssistantService.handle(msg: Message) -> Response
```

### Models Contract (`src/assistant_core/models.py`)

- **`Intent(str, Enum)`**:
  - `GREETING = "greeting"`
  - `FEE = "fee"`
  - `OFFICE = "office"`
  - `RULE = "rule"`
  - `UNKNOWN = "unknown"`

- **`Message(BaseModel)`**:
  - `text: str`: min_length=1, max_length=2000, rejects whitespace-only.
  - `session_id: str`: defaults to `"local"`.

- **`Source(BaseModel)`**:
  - `id: str`: unique source identifier (e.g. `"H26-5.3"`).
  - `title: str`: human-readable title.

- **`Response(BaseModel)`**:
  - `answer: str`: output message string.
  - `intent: Intent`: recognized intent.
  - `sources: list[Source]`: list of sources.
  - `degraded: bool`: boolean flag indicating fallback utilization.

- **`Rule(BaseModel)`**:
  - `id: str`
  - `title: str`
  - `text: str`

---

## Internal Component Contracts

### 1. Router (`src/assistant_core/router.py`)
```python
route(text: str, office_names: set[str]) -> Intent
```
- Evaluation precedence: Greeting → Fee/Tuition → Office → Rule.
- Strips punctuation (`?!.`) and whitespace. Case-insensitive.

### 2. Tools (`src/assistant_core/tools.py`)
```python
parse_credits(text: str) -> tuple[int, int]
tuition(credits: int, retake: int, rate: int, retake_multiplier: float, max_credits: int) -> int
```
- Pure functions, deterministic arithmetic.
- Rejects negative credits, negative retakes, or out-of-bounds credit loads with `InvalidRequest`.

### 3. Knowledge (`src/assistant_core/knowledge.py`)
```python
OfficeDirectory.from_csv(path: Path) -> OfficeDirectory
OfficeDirectory.find(text: str) -> Office | None

Handbook.from_json(path: Path) -> Handbook
Handbook.search(query: str) -> Rule | None
Handbook.get_by_id(rule_id: str) -> Rule | None
```
- Missing files or invalid schemas raise `DataError`.
- No match returns `None`.

### 4. Responders (`src/assistant_core/responder.py`)
```python
class Responder(Protocol):
    def explain(self, question: str, rule: Rule) -> str: ...
```
- `TemplateResponder`: Returns `f"{rule.title}: {rule.text}"`.
- `StubLLMResponder`: Returns formatted stub answer or raises `ProviderError` when `fail=True`.


## Integration status after PR #1

These interfaces now exist in the integrated core; this is no longer a pending skeleton.
Settings, load_settings, constructor injection and CLI wiring are documented in architecture.md.
Remaining deviations are tracked in lab3/open-items.md. The initial greeting punctuation extension and
--json/--log-level/--credit-rate/rule-ID helpers were introduced by PR1; do not claim they are new work
in a later H1 assignment without a genuinely distinct change and supporting personal evidence.
