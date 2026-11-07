# Lab 5 integration contract — draft

This contract prepares the API integration. Implementation and review by the team are still pending.
Reference: CSC10014 public materials Lab 5, commit `d795a1a09f430d83b0c69b45da1689984a1254b5`.

## Repository interface

`assistant_api.db.Repository` is responsible for database operations:

- `record_interaction(raw_session, request_id, intent, topic, resolved, degraded, latency_ms) -> None` records the hashed session and interaction together.
- `add_feedback(request_id, rating, comment) -> Feedback | None` saves feedback for an existing interaction; returns `None` when the ID is unknown.
- `list_feedback(limit=100) -> list[Feedback]` returns newest first, at most `limit` items.
- The starter also provides `intent_stats()` for the admin stats endpoint.

The API will accept an injected repository for isolated tests. Without one, it will create a repository from validated settings. Database setup and lifetime must be agreed with the DB/config owners before integration.

## HTTP behavior

`POST /v1/chat` generates one request ID, records it with metadata, then returns that same ID. Raw message and raw session ID are not stored. `POST /v1/feedback` returns 201 for an existing interaction and 404 for an unknown ID. `GET /v1/feedback` remains admin-protected and returns stored records newest first.

The existing offices, weather, rate limiting, error response and admin header behavior remain covered by regression tests. Existing tests that submit arbitrary feedback IDs need to create a chat first; add an explicit 404 test for unknown IDs.

## Integration acceptance

1. Tests use an injected, isolated database; restart coverage uses a temporary file with a new app/engine.
2. A real server restart with the same database retains feedback.
3. Check configuration and database contents for disclosure of raw session/message or salt; feedback comments can themselves contain sensitive information, so demonstrations use synthetic content.
4. Run the complete existing test suite, Lab 5 tests, lint and format checks before merge.
