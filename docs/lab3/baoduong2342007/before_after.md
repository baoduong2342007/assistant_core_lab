# Dương — initial maintainability worksheet

Scope: repository foundation and packaging only. Runtime refactor not implemented.
Before evidence: ../baseline.md and ../baseline-evidence.json.

| Question | Before | After |
| --- | --- | --- |
| Change credit rate | RATE assignment in monolith | Pending Huy config + Minh tools + Dương integration |
| Tests offline/no API key | Local stub, but sleeps/random; fake key is unused | Packaging checks offline after dependency install; behavior tests pending |
| Missing handbook.json | Bare except prints warning and keeps global state | Pending Quyền DataError implementation |
| Secret printed/logged | Fake hard-coded key and prompt printed by llm() | Core logging pending Huy |
| Find fee logic | In handle(); no timed newcomer measurement | Module boundaries documented; implementation pending |
| Module-level assigned names | 9, AST Assign count | No runtime module implementation yet |
| Bare except handlers | 3 | No runtime module implementation yet |
| Longest function | handle: 56 inclusive lines | No runtime functions yet |
| Ruff diagnostics | 8 with explicit isolated rules | See PR checks for skeleton only |
| Swap LLM without changing service | handle directly calls llm | Responder contract proposed; implementation pending |

## Code smells and owners

- Hard-coded key/config: Huy config; remove key dependency from stub.
- Mutable global offices/handbook/history: Quyền loaders and Dương dependency injection.
- Bare except on load: Quyền DataError; interactive input: Dương CLI.
- Oversized handle: Dương service delegating to module owners.
- Mixed print/log/answer stream: Huy logging, Dương CLI.
- Fee parsing/calculation mixed with I/O: Minh pure tools.
- String path concatenation/unclosed JSON file: Quyền pathlib/context managers.
- Random failures and sleep: Bảo deterministic responders.
- Print-only manual tests: each owner writes assertions; Bảo shared fixtures.
- Repeated routing in handle/stats: Minh router; history/stats outside core scope.

## Three reflections (current stage)

The foundation now separates untouched reference material from the future package.
Coordination is more complex because interfaces must be reviewed before parallel implementation.
Next I would integrate service and CLI only after the owners deliver agreed contracts.
