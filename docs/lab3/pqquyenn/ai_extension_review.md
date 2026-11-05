# H1: list loaded handbook rule titles

Implemented in PR31 on behalf of the group at Dương's request, with Codex assistance. This report replaces the earlier unverified claims; it does not assert that Quyền independently reviewed AI output.

## Actual behavior

`python -m assistant_core --list-rules` returns handbook titles in loaded data order. `--show-sources` includes source IDs; `--json` returns the normal Response shape. The command exits after listing and rejects a simultaneous query. Empty data returns an explicit message.

## Concrete improvements made and verified

1. Connected the existing `Handbook.rules` accessor to `AssistantService.list_rules()` and an actual CLI flag. The accessor alone did not provide a user-facing feature.
2. Projected loaded Rule objects into new Response/Source values. The earlier report incorrectly called Rule frozen: it is a mutable Pydantic model. Listing returns text and independent Source values; it does not expose mutable Rule objects or reread files.
3. Added deterministic behavior for empty data, JSON output and conflicting query arguments, with tests proving stable order and no provider/search call. This separates data retrieval, orchestration and display.

These are evidenced assisted changes in the code and tests, not invented actions by the owner. Initial historical prompt/output is not reconstructed. Owner reading, explanation and personal authorship requirements remain subject to the owner's confirmation.

## Validation

See `tests/test_h1_list_rules.py` for loaded ordering, empty result, CLI JSON and invalid argument combinations. Existing Week 3 tests remain unchanged; regression results are recorded in the PR.
