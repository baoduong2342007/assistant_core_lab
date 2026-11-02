# Lab 4 — API Contract

| Method | Path | Request | Success | Errors | Caller |
|---|---|---|---|---|---|
| GET | /health | — | 200: status, version | — | ops, UI |
| POST | /v1/chat | message: nonblank string, 1–2000 chars; optional session_id up to 64 | 200: answer, intent, sources, degraded, request_id | 422 invalid_request; 429 too_many_requests | UI, tests |
| POST | /v1/feedback | request_id 1–64 chars, rating -1..1, optional comment up to 500 | 201: input plus id and created_at (UTC) | 422 invalid_request | UI |
| GET | /v1/feedback | X-API-Key header | 200: feedback array | 401 missing_or_invalid_api_key | staff |
| GET | /v1/weather | — | 200: temperature_c, wind_kmh, description, observed_at, stale | 503 weather_service_unavailable | UI |
| GET | /v1/offices | — | 200: name-sorted array of name, room, hours | — | UI |

## Contract Specifications & Error Handling

- **Request Validation:** Input validation is enforced by Pydantic schemas. Any validation failure yields HTTP `422 Unprocessable Entity` with JSON body:
  ```json
  {
    "error": {
      "code": "invalid_request",
      "message": "<field_location>: <error_message>"
    }
  }
  ```
  Specifically for `POST /v1/chat`, messages consisting solely of whitespace characters are rejected with `422 invalid_request` rather than triggering unhandled 500 domain exceptions.
- **Rate Limiting (Part F):** Chat requests are rate-limited per client IP address (`request.client.host`) using an in-memory sliding window (`RateLimiter`) configured via `RATE_LIMIT_PER_MIN` (default 30). Requests exceeding the rate limit return HTTP `429 Too Many Requests`:
  ```json
  {
    "error": {
      "code": "too_many_requests",
      "message": "Too many requests"
    }
  }
  ```
- **Admin Authentication:** The endpoint `GET /v1/feedback` requires the header `X-API-Key` matching `Settings.api_admin_key`. Missing or mismatched keys return HTTP `401 Unauthorized`:
  ```json
  {
    "error": {
      "code": "missing_or_invalid_api_key",
      "message": "Missing or invalid API key"
    }
  }
  ```
- **External Weather Integration:** `GET /v1/weather` proxies Open-Meteo with a default 3-second timeout, 1 retry, and in-memory TTL caching (600s). In the event of an upstream outage:
  - If a cached report is present, it returns HTTP `200` with `stale: true`.
  - If no cache exists, or upstream returns malformed JSON payloads, it raises `ExternalServiceError`, mapped by FastAPI to HTTP `503 Service Unavailable`:
    ```json
    {
      "error": {
        "code": "weather_service_unavailable",
        "message": "Weather service unavailable"
      }
    }
    ```
- **Offices Directory (H1):** `GET /v1/offices` queries `OfficeDirectory.all()`, returning university offices sorted alphabetically by name.
- **Feedback Storage:** In-memory list (RAM) for Lab 4; persistence to PostgreSQL/SQLite is scheduled for Lab 5.

The starter and worksheet were adapted from CSC10014 public_materials, commit `a848a96d44876d4baee5eabe645114cf56d0b82f`; the existing Lab03 core remains the source of business logic.
