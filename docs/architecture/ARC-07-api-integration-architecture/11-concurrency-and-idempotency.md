# 11. Concurrency and Idempotency Architecture

## 1. Optimistic Concurrency Control
- Stateful resources (menus, themes, design configs) maintain a `row_version` integer.
- The server provides an `ETag: W/"<version>"` header on GET requests.
- Mutating requests must provide `If-Match: "<version>"`. Stale updates receive `409 Conflict` or `412 Precondition Failed`.

## 2. Idempotency Keys
- Non-idempotent operations (publishing, billing) accept `Idempotency-Key` header.
- Cached results returned on duplicate key submissions.
