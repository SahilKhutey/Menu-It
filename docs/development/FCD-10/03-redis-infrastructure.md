# FCD-10 — Redis Infrastructure & Lifecycle

**Milestone:** `v1.0.0-fcd10`  
**Phase:** FCD-10 — Caching, Background Jobs & Event Infrastructure  
**Author:** AI Architecture & Core Engineering Team  
**Status:** Approved  

---

## 1. Connection Pool Architecture

Redis connectivity is managed via `ConnectionPool` in `menu_it.infrastructure.redis.client`:
- **Pool Settings:** Configured via typed Pydantic `Settings` (`redis_url`, `redis_max_connections=30`, `redis_connect_timeout=5`, `redis_socket_timeout=5`, `health_check_interval=30`).
- **Singleton Lifecycle:** One managed pool per process; connections are multiplexed and reused across requests.
- **Graceful Termination:** `close_redis_client()` safely terminates the pool during application shutdown.

---

## 2. Namespace & Key Isolation

To prevent collision between caching, queue broker data, and test environments:
- **Cache Keys:** `menu-it:v1:org:{org_id}:{resource}:{id}` and `menu-it:v1:public:{resource}:{id}`.
- **Worker Queues:** `menu-it:jobs:default`.
- **Environment Prefixes:** Configurable via `REDIS_KEY_PREFIX` (e.g. `menu-it:dev`, `menu-it:test`).
