# Lab 3 — AI Extension Review (H1)

**Author:** Phạm Quốc Bảo (`simble2k`)  
**Assigned Feature:** Exact rule lookup by ID (`Handbook.get_by_id` / `find_rule_by_id`)  
**Target Module:** Knowledge & Service integration layer  
**Reviewer:** Dương (`baoduong2342007`)

---

## 1. Initial Prompt Provided to AI Assistant

```text
Please implement an exact regulation lookup function by ID for the student handbook knowledge layer.
The function should allow users to look up a rule by passing an identifier such as 'H26-5.3', and
integrate cleanly with the AssistantService response structure (Source attachment and degraded fallback).
```

### Initial Proposal by AI:
```python
def get_rule(rules, id):
    for r in rules:
        if r.id == id:
            return r
    raise Exception(f"Rule {id} not found")
```

---

## 2. Code Review and Three Concrete Improvements

| # | What the AI Generated | Problem Identified | What I Changed | Why |
|---|---|---|---|---|
| **1** | Strict case-sensitive comparison `r.id == id`. | Users typing lowercase or mixed casing (e.g. `h26-5.3` or with whitespace `  H26-5.3 `) fail to match valid rules. | Applied `.strip().lower()` normalization to both target `rule.id` and the search query identifier. | Enhances user experience and prevents silent lookup failures caused by formatting discrepancies. |
| **2** | Raised a bare `Exception(f"Rule {id} not found")`. | Violates domain exception hierarchy and crashes caller instead of cleanly routing to `Intent.UNKNOWN`. | Replaced the exception with returning `None`, allowing caller service to return an informative response with empty sources. | Adheres to domain contract boundaries where missing search hits are valid outcomes, not fatal program crashes. |
| **3** | No handling for empty queries or empty collections. | Crashed or raised generic exceptions when given empty inputs, violating clean code guidelines. | Added guard clauses returning `None` immediately when `rule_id` is empty, whitespace-only, or collection is empty. | Prevents unnecessary iterations, guarantees idempotent execution, and satisfies Ruff `BLE001` guidelines. |

---

## 3. Corrected runtime verification — 2026-10-25

Dương used Codex to fix the reviewed branch. The earlier implementation and fallback helper lived only in tests. Production now uses `Handbook.get_by_id` from `AssistantService._rule`; the CLI can query `python -m assistant_core --json H26-5.3` (add `--fail-provider` to exercise fallback).

The existing lookup already returned None on misses. This correction adds an explicit blank-ID guard and normalizes stored IDs as well as queries. These are corrections made with Codex, not three new manual improvements claimed for Bảo. Original prompt/review claims above are retained as Bảo's earlier report and require his confirmation.

`tests/test_h1_rule_by_id.py` now imports the real Handbook, calls the real service, and runs CLI subprocess cases for success/failure. It covers exact/case/whitespace matching, unknown/partial/empty IDs, empty handbook, source retention and degraded flags. `tests/test_fallback.py` calls the real service using shared responder fixtures, with runtime protocol checks. No parallel product implementation remains in tests.

Local validation: 107 tests passed; Ruff check/format/BLE passed. Runtime fixes and evidence corrections by Dương with Codex; original responder/fixture work remains credited to simble2k.
