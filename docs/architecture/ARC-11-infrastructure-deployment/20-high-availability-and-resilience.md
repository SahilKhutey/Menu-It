# 20 — High Availability & Resilience
**ARC-11: Infrastructure & Deployment Architecture**

## 1. Graceful Degradation Strategy
- **Redis Outage:** If Redis becomes unreachable, API rate limiting switches to in-memory token buckets, and caching is bypassed without throwing 500 Internal Server Errors.
- **Worker Failure:** If a worker crashes, in-flight transactional outbox events remain safely persisted in the database and are reclaimed by the next active polling cycle.
- **Container Restarts:** All services configured with `restart: unless-stopped`.\n