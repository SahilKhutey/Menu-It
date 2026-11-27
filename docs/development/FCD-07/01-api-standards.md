# FCD-07 §01 — API Standards & Conventions

## 1. Resource Naming Conventions

All Menu-It APIs adhere to RESTful, resource-oriented conventions:
- Use **plural lowercase nouns** for resources (e.g. `/restaurants`, `/organizations`, `/users`).
- Use **kebab-case** for multi-word paths (e.g. `/operating-hours`, `/audit-events`).
- Identify single entities via URL path parameters using UUIDs (e.g. `/api/v1/restaurants/{restaurant_id}`).
- For non-CRUD business actions, use explicit verb sub-paths (e.g. `POST /api/v1/restaurants/{restaurant_id}/activate`, `POST /api/v1/auth/password/reset`).

## 2. HTTP Method Semantics

| Method | Idempotent | Safe | Typical Status | Usage |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | Yes | Yes | 200 OK | Retrieve resource or paginated collection |
| `POST` | No | No | 201 Created / 200 OK | Create subordinate resource or trigger business action |
| `PUT` | Yes | No | 200 OK | Replace entire resource state |
| `PATCH` | Yes | No | 200 OK | Partially update specific resource attributes |
| `DELETE`| Yes | No | 200 OK / 204 No Content | Remove or soft-delete resource |
| `OPTIONS`| Yes | Yes | 200 OK | CORS preflight protocol negotiation |

## 3. HTTP Status Codes

- `200 OK`: Successful synchronous read or update.
- `201 Created`: Resource successfully created (includes Location header where applicable).
- `202 Accepted`: Asynchronous or queued operation accepted.
- `204 No Content`: Successful operation with empty body.
- `400 Bad Request`: Malformed request syntax or unparseable payload.
- `401 Unauthorized`: Missing or invalid bearer token / session.
- `403 Forbidden`: Authenticated identity lacks required permissions.
- `404 Not Found`: Resource unavailable in caller's permitted scope.
- `409 Conflict`: Business rule violation, unique constraint collision, or invalid lifecycle transition.
- `412 Precondition Failed`: Version concurrency precondition failed.
- `422 Unprocessable Content`: Schema or field-level validation failure.
- `429 Too Many Requests`: Rate limit threshold exceeded.
- `500 Internal Server Error`: Unexpected runtime failure (details sanitized).
- `503 Service Unavailable`: Temporary downstream dependency outage (database or cache).

## 4. URL Path Versioning

API versioning is strictly implemented via URL paths:
`/api/v1/...`
Breaking changes require incrementing the version path (`/api/v2/...`). Header-based or query-parameter versioning is prohibited.

## 5. Security & Request Headers

- `X-Request-ID`: Client-provided or server-generated correlation UUID for end-to-end tracing.
- `Authorization`: `Bearer <token>` for authenticated endpoints.
- `Idempotency-Key`: Optional UUID for safe retry of state-modifying requests.
- `Content-Type`: `application/json` for all request and response payloads with a body.
