# FCD-10 — Architecture Decision Records (ADRs)

**Milestone:** `v1.0.0-fcd10`  
**Phase:** FCD-10 — Caching, Background Jobs & Event Infrastructure  
**Author:** AI Architecture & Core Engineering Team  
**Status:** Approved  

---

## Index of Architecture Decision Records

### FCD10-ADR-001: Redis as Primary Cache & Execution Transport
- **Context:** Need low-latency distributed caching and lightweight task queue broker.
- **Decision:** Adopt Redis with managed connection pools.
- **Consequence:** Redis is ephemeral; PostgreSQL remains the durable source of truth.

### FCD10-ADR-002: ARQ as Asynchronous Python Worker Framework
- **Context:** FastAPI and SQLAlchemy are fully async. Celery requires synchronous adapters and heavy dependencies.
- **Decision:** Adopt ARQ for native async Python worker execution.

### FCD10-ADR-003: PostgreSQL as Durable Event, Job, and DLQ Store
- **Context:** Message loss in Redis queues must not lose business work.
- **Decision:** Store all job metadata, outbox events, and dead letters in PostgreSQL.

### FCD10-ADR-004: Transactional Outbox Pattern for Dual-Write Safety
- **Context:** API database writes and event publishing must not diverge.
- **Decision:** Write outbox events within the same PostgreSQL transaction as business state changes.

### FCD10-ADR-005: Consumer Inbox Table for At-Least-Once Idempotency
- **Context:** Network partitions or retries can deliver the same event multiple times.
- **Decision:** Insert `(consumer_name, event_id)` into `processed_events` within consumer transaction.

### FCD10-ADR-006: Exponential Backoff with Jitter for Failure Retries
- **Context:** Linear retries cause thundering herds against failing services.
- **Decision:** Implement exponential backoff formula with bounded max delay and random jitter.

### FCD10-ADR-007: Explicit Tenant-Context Propagation & Transaction-Local RLS
- **Context:** Workers executing tenant jobs must never access unauthorized tenant rows.
- **Decision:** Propagate `JobContext` explicitly; workers set transaction-local RLS via `set_database_tenant_context()`.

### FCD10-ADR-008: Database-Backed Persistent Schedules
- **Context:** In-memory schedulers lose state on deployment or restart.
- **Decision:** Persist schedule definitions and execution history in `scheduled_jobs` and `scheduled_job_runs`.

### FCD10-ADR-009: Tenant-Aware Cache Key Generation
- **Context:** Cache keys must guarantee zero cross-tenant key leakage or collision.
- **Decision:** Mandatory `menu-it:v1:org:{org_id}:{resource}:{id}` key structure validated server-side.

### FCD10-ADR-010: Separate Worker Process Deployment
- **Context:** CPU-heavy or slow tasks must not block HTTP API request throughput.
- **Decision:** Deploy ARQ workers as independent standalone processes.
