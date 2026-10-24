# Lab 3 — AI Extension Review

**Author:** Nguyễn Tấn Bảo (`simble2k`)  
**Feature:** Exact rule lookup by ID (`Handbook.get_by_id`)

---

## 1. Prompt Used
```text
Add exact rule ID search to Handbook so users can retrieve regulations by specific identifiers like 'H26-5.3'.
```

---

## 2. Code Review and Three Concrete Improvements

| # | What the AI Generated | Problem Found | What I Changed | Why |
|---|---|---|---|---|
| 1 | Case-sensitive string equality check `r.id == rule_id`. | Failed when users typed lowercase ids like `h26-5.3`. | Added `.strip().lower()` normalization on both rule id and search query. | Enhances user experience and robustness against casing differences. |
| 2 | Returned a generic string message when rule wasn't found. | Inconsistent with `search()` contract which returns `Rule | None`. | Returned `None` when no rule matched. | Preserves uniform API semantics across all lookup methods. |
| 3 | Threw a generic `Exception` if handbook was empty. | Violated `BLE001` and leaked unhandled exceptions. | Gracefully returned `None` without crashing. | Follows clean code error handling guidelines. |
