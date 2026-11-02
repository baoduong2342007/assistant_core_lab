# Lab 4 — API contract

| Method | Path | Request | Success | Errors | Caller |
|---|---|---|---|---|---|
| GET | /health | — | 200: status, version | — | ops, UI |
| POST | /v1/chat | message: nonblank string, 1–2000 chars; optional session_id up to 64 | 200: answer, intent, sources, degraded, request_id | 422 invalid_request; 429 too_many_requests | UI, tests |
| POST | /v1/feedback | request_id 1–64 chars, rating -1..1, optional comment up to 500 | 201: input plus id and created_at (UTC) | 422 invalid_request | UI |
| GET | /v1/feedback | X-API-Key or X-Admin-Key header | 200: feedback array | 401 missing_or_invalid_api_key | staff |
| GET | /v1/weather | — | 200: temperature_c, wind_kmh, description, observed_at, stale | 503 weather_service_unavailable | UI |
| GET | /v1/offices | — | 200: name-sorted array of name, room, hours | — | UI |

Validation errors use `error.code = invalid_request`; the client can show a correction prompt. Authentication failures need a sign-in or access message; 503 may be retried later. An incompatible change to field meanings or types could require a new API version. An unknown route currently uses Starlette's 404 `detail` shape. Feedback is in memory and is lost on restart. Weather may return stale cached data with `stale=true` after an upstream failure.

The starter and worksheet were adapted from CSC10014 public_materials, commit `a848a96d44876d4baee5eabe645114cf56d0b82f`; the existing Lab03 core remains the source of business logic.

Chat rate limiting uses the client address and `RATE_LIMIT_PER_MIN` (default 30). Limits are maintained in memory per server process; requests exceeding the limit return 429.
