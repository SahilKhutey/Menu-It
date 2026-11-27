# FCD-10 — Scope, Dependencies & Ownership

**Milestone:** `v1.0.0-fcd10`  
**Phase:** FCD-10 — Caching, Background Jobs & Event Infrastructure  
**Author:** AI Architecture & Core Engineering Team  
**Status:** Approved  

---

## 1. Phase Mission

Phase **FCD-10** establishes the asynchronous execution, caching, and event infrastructure required by Menu-It:
- Redis-backed distributed caching and cache-aside abstraction.
- Asynchronous background worker orchestration via ARQ.
- Exponential backoff retry policies and persistent dead-letter handling.
- Event-driven transactional outbox and consumer inbox deduplication.
- Database-backed persistent scheduling with IANA timezone awareness.
- Strict multi-tenant context propagation and PostgreSQL Row-Level Security isolation.

---

## 2. Dependencies & Invariants

| Phase | Dependency | Invariant Upheld |
| :--- | :--- | :--- |
| **FCD-02** | Application lifecycle & health probes | Graceful Redis connection startup & shutdown |
| **FCD-03** | Database foundation & repositories | Async SQLAlchemy 2.x sessions & Alembic migrations |
| **FCD-04** | Multi-tenant core foundation | `set_database_tenant_context` with transaction-local RLS |
| **FCD-05** | Identity & authorization | Authenticated principal attribution on internal job APIs |
| **FCD-06** | Domain foundation | Decimal/Money and UTC-only datetime serialization |
| **FCD-07** | API communication infrastructure | Standard `APIResponse[T]` envelope on `/api/v1/internal` |
| **FCD-09** | Platform services container | Encapsulated service composition in `PlatformServices` |

---

## 3. Explicit Ownership Boundaries

| Capability | Owning Phase | FCD-10 Responsibility |
| :--- | :--- | :--- |
| Caching | FCD-10 | `CacheBackend`, `RedisCacheBackend`, `CacheService`, TTLs |
| Background Jobs | FCD-10 | `JobService`, `JobEnvelope`, `WorkerSettings`, registry |
| Retry & DLQ | FCD-10 | `calculate_retry_delay`, `DeadLetterService`, replay API |
| Event Infrastructure | FCD-10 | `EventOutboxModel`, `OutboxDispatcher`, `EventInbox` |
| Persistent Scheduling | FCD-10 | `ScheduledJobModel`, `SchedulingService`, `JobScheduler` |
| Observability & Tracing | FCD-11 | FCD-10 emits operational metrics; FCD-11 owns OTel/dashboards |
