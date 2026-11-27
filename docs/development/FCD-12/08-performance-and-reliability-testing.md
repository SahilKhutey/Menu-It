# FCD-12 · Document 08: Performance & Reliability Testing

**Phase:** FCD-12 — Automated Testing & CI/CD Foundation  
**System:** Menu-It Restaurant SaaS Platform  
**Status:** Completed & Approved  
**Date:** 2026-11-26  

---

## 1. Performance Testing with k6

Menu-It uses k6 for automated API load and smoke testing (`tests/performance/api-smoke.js`):
- Verifies endpoint latencies under concurrent traffic:
  - 95th percentile latency: `< 500ms`.
  - HTTP failure rate: `< 1.0%`.
- Validates `/api/v1/health` and `/api/v1/system/info`.

---

## 2. Reliability Scenarios

Automated and manual chaos testing verifies:
1. **Redis Node Outage:** `RedisRateLimiter` falls back to `InMemoryRateLimiter`; cache degrades gracefully to direct database queries.
2. **Third-Party Outage:** `CircuitBreaker` trips to OPEN state on consecutive failures, fast-failing requests to avoid thread pool exhaustion.
3. **Database Transaction Contention:** Dead-letter job queues and exponential backoff prevent cascading retries.
