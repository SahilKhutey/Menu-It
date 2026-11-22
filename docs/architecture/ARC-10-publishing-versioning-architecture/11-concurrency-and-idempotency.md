# ARC-10 §11: Concurrency & Idempotency
**Race Condition Elimination & Replay Protection**

## 1. Idempotency Keys
Mutating requests accept header `Idempotency-Key: <UUID>`:
- Keys are scoped by `organization_id:menu_id:operation:key`.
- Request fingerprint is computed via SHA-256.
- If repeated with identical payload, the cached confirmed publication is returned.
- If repeated with conflicting payload, HTTP 409 Conflict (`IDEMPOTENCY_KEY_REUSED`) is returned.

## 2. Menu-Level Locking
Menu row locking ensures concurrent publish requests are strictly serialized. Only one request wins the lock; the second re-checks state and handles conflict gracefully.
