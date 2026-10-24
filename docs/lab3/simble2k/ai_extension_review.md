# Lab 3 — AI Extension Review (H1)

**Author:** Nguyễn Tấn Bảo (`simble2k`)  
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

## 3. Test & Verification Evidence

All test cases implemented in `tests/test_h1_rule_by_id.py`:
- `test_find_rule_by_id_exact_match`: Verifies exact ID lookup.
- `test_find_rule_by_id_case_insensitive`: Confirms `h26-5.3` matches `H26-5.3`.
- `test_find_rule_by_id_whitespace_stripping`: Confirms stripped search query.
- `test_find_rule_by_id_not_found`: Confirms non-existent ID returns `None`.
- `test_execute_lookup_by_id_fallback_on_provider_error`: Proves provider failure initiates fallback, retains `Source(id="H26-5.3")`, and flags `degraded=True`.
