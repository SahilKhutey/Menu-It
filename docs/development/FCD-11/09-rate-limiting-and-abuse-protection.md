# FCD-11 · Document 09: Rate Limiting, Throttling & Abuse Prevention

**Phase:** FCD-11 — Security, Reliability & Observability Foundation  
**System:** Menu-It Restaurant SaaS Platform  
**Status:** Completed & Approved  
**Date:** 2026-11-26  

---

## 1. Rate Limiting Architecture

Menu-It implements distributed rate limiting to guard against denial-of-service, brute force, and runaway traffic:

- **Engine:** `RedisRateLimiter` utilizing Redis sorted sets (`ZADD`, `ZREMRANGEBYSCORE`, `ZCARD`) for atomic sliding-window accounting.
- **Degradation / Fallback:** If Redis is temporarily unreachable or unconfigured, the limiter gracefully degrades to `InMemoryRateLimiter` without dropping traffic.
- **Rate Limit Response:** When an endpoint quota is exceeded, the server returns HTTP 429 Too Many Requests with standard response headers:
  - `Retry-After: <seconds>`
  - `X-RateLimit-Limit: <quota>`
  - `X-RateLimit-Remaining: 0`
  - `X-RateLimit-Reset: <seconds>`

---

## 2. Quota Profiles

| Category | Default Quota | Window | Key Strategy |
| :--- | :--- | :--- | :--- |
| **Authentication Endpoints** | 10 requests | 60 seconds | `auth:ip:{client_ip}` |
| **Password Reset** | 3 requests | 300 seconds | `reset:email:{email_hash}` |
| **Public Menu Browsing** | 120 requests | 60 seconds | `public:ip:{client_ip}` |
| **Tenant API Endpoints** | 600 requests | 60 seconds | `tenant:org:{organization_id}` |
| **File Uploads** | 20 uploads | 60 seconds | `upload:org:{organization_id}` |
