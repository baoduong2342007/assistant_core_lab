# H1: plain-text source display

Owner: Dương (`baoduong2342007`). Codex assisted implementation and report correction at Dương's request. The implemented extension is `--show-sources`, merged in PR27. `--json` existed before this work; the old report incorrectly presented it as a new extension.

## Actual implementation and review

The CLI passes `show_sources` into formatting of the Response returned by `service.handle(Message)`. Source IDs and titles are displayed below the plain-text answer, with interactive mode supported. JSON output retains its existing shape.

Three concrete assisted safeguards present in the implementation and tested:

1. Format the sources returned by the service rather than performing a second handbook lookup; provider fallback retains the actual source IDs/titles.
2. Reject `--json --show-sources` as a redundant option combination before handling a message, keeping the JSON contract unambiguous.
3. Keep the answer unchanged when no sources exist, and apply the same formatter to one-shot and interactive queries.

Evidence: `tests/test_cli_show_sources.py` and PR27. These are code-level checks performed with AI assistance; this report does not reconstruct an unavailable initial AI proposal or claim Dương independently made three review changes. Dương should verify that the retained evidence meets the instructor's personal H1 requirements.
