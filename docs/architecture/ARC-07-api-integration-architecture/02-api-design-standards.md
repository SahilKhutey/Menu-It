# 02. API Design Standards

## 1. URI Naming and Formatting
- **Base URI:** `/api/v1`
- **Resource Collections:** Plural lowercase nouns (e.g., `/organizations`, `/restaurants`, `/menus`, `/categories`, `/items`).
- **Hierarchy:** Natural nested paths for ownership (e.g., `/api/v1/restaurants/{restaurant_id}/menus`).
- **Path Identifiers:** Canonical UUIDv4 strings.

## 2. HTTP Method Semantics
| Method | Idempotent | Safe | Usage | Expected Status Codes |
|---|---|---|---|---|
| `GET` | Yes | Yes | Retrieve resource or collection | 200 OK, 404 Not Found |
| `POST` | No | No | Create resource or initiate action | 201 Created, 202 Accepted, 409 Conflict, 422 Unprocessable |
| `PATCH` | No | No | Partial update of resource fields | 200 OK, 404 Not Found, 409 Conflict |
| `PUT` | Yes | No | Replace resource or configuration | 200 OK, 201 Created |
| `DELETE` | Yes | No | Remove or soft-delete resource | 204 No Content, 404 Not Found |

## 3. Headers Standard
- `X-Request-ID`: Correlation identifier passed through entire pipeline.
- `X-Organization-ID`: Tenant selector header evaluated strictly against user memberships.
- `ETag` & `If-Match`: Concurrency token for stateful mutations.
- `Idempotency-Key`: UUIDv4 token for safe mutation retries.
