# Lab 3 — AI Extension Review

**Author:** Phan Quỳnh Quyền (`pqquyenn`)  
**Feature:** List available academic handbook regulations

---

## 1. Prompt Used
```text
Add a method to Handbook that allows retrieving all rule titles and summaries so the assistant can list what rules are available.
```

---

## 2. Code Review and Three Concrete Improvements

| # | What the AI Generated | Problem Found | What I Changed | Why |
|---|---|---|---|---|
| 1 | Re-read `handbook.json` from disk every time the list method was called. | Caused repeated disk I/O on every request and broke if file moved after startup. | Returned a copy of the in-memory `self._rules` list loaded at initialization. | Optimizes performance and adheres to load-once semantics. |
| 2 | Returned mutable references to internal rule objects. | Callers could inadvertently mutate rule text or titles in memory. | Returned frozen `Rule` dataclass/model copies. | Protects knowledge repository integrity. |
| 3 | Hardcoded a print statement inside `Handbook`. | Violated separation of concerns by mixing UI output with domain data retrieval. | Provided pure data return method `Handbook.rules`. | Allows caller (CLI or API) to decide how to format and display the rules. |
