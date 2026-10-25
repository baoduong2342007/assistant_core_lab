# Test ownership and coverage

PR #1 introduced the original 71 tests. Dương's PR #16 adds 19 acceptance/regression cases
in test_cli_contract.py and test_service.py for a total of 90.
Coverage includes invalid startup/request/usage exits, EOF/quit/blank lines and interactive recovery,
CLI log/answer streams, rule sources on success/fallback, unknown, invalid fee guidance and propagation
of programming errors. Each subprocess uses isolated environment settings and a timeout.
Other owners retain responsibility for their module acceptance gaps; see docs/lab3/open-items.md.
