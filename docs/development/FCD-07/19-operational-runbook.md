# FCD-07 §19 — Operational Runbook & Production Diagnostics

## 1. Routine Maintenance

### Idempotency Records Pruning
Idempotency records have an expiration date (`expires_at`, default 24 hours). Periodic cleanup can be executed via:
```python
from menu_it.infrastructure.idempotency.service import IdempotencyService
# Call periodically via scheduled cron or Celery worker
await IdempotencyService.purge_expired(session)
```

### Rate Limiter Key Management
When running with `RedisRateLimiter`, keys expire automatically with TTL (`window_seconds + 5`). In-memory rate limiting stores history locally and discards expired timestamps upon each check or via `limiter.reset(key)`.

---

## 2. Common Incidents & Resolution

### Incident: Client receives 409 Conflict with `IDEMPOTENCY_CONFLICT`
- **Cause:** Client reused an idempotency key (e.g. from an earlier request) but changed the payload body, method, or path.
- **Resolution:** Instruct client to generate a new UUID v4 key for every distinct intent. Idempotency keys must only be retransmitted on exact retries of the original payload.

### Incident: Client receives 429 Too Many Requests
- **Cause:** Rate limits exceeded by client IP, tenant, or user.
- **Resolution:** Inspect response headers `Retry-After` and `X-RateLimit-Reset`. Advise client to implement exponential backoff with jitter.

### Incident: 404 on Existing Restaurant Resource
- **Cause:** Request is missing `X-Organization-ID` or authenticated user is not an active member of the restaurant's owning organization.
- **Resolution:** Verify user organization memberships and check that the client sends the correct tenant ID.
