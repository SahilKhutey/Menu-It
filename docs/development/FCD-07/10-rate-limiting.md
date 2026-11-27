# FCD-07 §10 — Rate Limiting Infrastructure & Throttling Policies

## 1. Objectives & Threat Mitigation

Rate limiting protects Menu-It endpoints against:
1. Denial-of-service (DoS) attempts and bot exhaustion.
2. Credential stuffing on authentication endpoints (`/api/v1/auth/login`).
3. Tenant resource starvation in multi-tenant environments.

---

## 2. Sliding Window Architecture

The rate limiter supports two interchangeable implementations conforming to `RateLimiter`:
- `InMemoryRateLimiter`: Thread-safe and asyncio-safe sliding window log using timestamps stored in a `collections.deque` guarded by `asyncio.Lock`.
- `RedisRateLimiter`: Distributed sliding window implementation using Redis atomic commands (`ZREMRANGEBYSCORE`, `ZCARD`, `ZADD`) with automatic local in-memory fallback on connection failure.

---

## 3. Rate Limit Key Strategies

| Strategy | Function | Target Routes |
| :--- | :--- | :--- |
| **IP-Based** | `get_ip_rate_key` | Public auth endpoints, health checks, unauthenticated probes |
| **Tenant-Based** | `get_tenant_rate_key` | Tenant-scoped data endpoints (`/api/v1/restaurants`) |
| **User-Based** | `get_user_rate_key` | User account modifications, sensitive session operations |

---

## 4. Response Headers & 429 Contract

When limits are evaluated:
- `X-RateLimit-Limit`: Maximum requests permitted within window.
- `X-RateLimit-Remaining`: Tokens remaining before throttling.
- `X-RateLimit-Reset`: Seconds remaining until oldest token expires.

When exhausted, HTTP `429 Too Many Requests` is returned with `Retry-After: <seconds>`:
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Please retry after some time.",
    "details": []
  },
  "meta": {
    "request_id": "...",
    "timestamp": "..."
  }
}
```
