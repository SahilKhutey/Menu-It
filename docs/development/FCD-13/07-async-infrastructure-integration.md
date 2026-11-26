# FCD-13 · Document 07 — Cache, Background Jobs, Events & Scheduling Integration

## 1. Objective
Validates that FCD-10 asynchronous infrastructure (Redis caching, ARQ workers, task registries, Transactional Outbox, and event consumers) functions predictably with application transactions, tenant security, and operational observability.

---

## 2. Asynchronous Architecture & Event Flow

```
1. Application Request (HTTP API)
   │
   ├──> Database Transaction Started
   │      ├──> Mutate Domain Aggregate
   │      └──> Publish to Outbox (OutboxEventPublisher)
   │
   └──> Transaction Committed
          │
          ▼
2. Background Poller / Outbox Dispatcher
   │
   └──> Dispatches to ARQ Worker via Redis
          │
          ▼
3. ARQ Task Execution (Worker)
   │
   ├──> Inject SystemTenantContext (explicit organization scope)
   ├──> Look up Handler in JOB_REGISTRY
   ├──> Idempotent Consumer Execution (ProcessedEventModel check)
   └──> Invalidate Relevant Cache Keys (CacheService)
```

---

## 3. Asynchronous Components & Guarantees

1. **`CacheService`:**
   - Provides JSON serialization with explicit TTLs.
   - Fault-tolerant fallback: Redis outages degrade safely to in-memory cache without crashing request lifecycles.
   - Resource-scoped invalidation (`invalidate_organization_resource`).
2. **`JOB_REGISTRY` & ARQ Worker:**
   - Central registry mapping task names to async handlers (`notification.send`, `file.process`, `menu.rebuild`).
   - Dynamic handler registration via `register_job_type`.
3. **Idempotent Outbox Processing:**
   - Duplicate event deliveries are detected via `processed_events` deduplication table.
   - Failed jobs retry with exponential backoff up to `max_tries` before moving to `dead_letter_jobs`.

---

## 4. Async Test Matrix

| Test ID | Test Scenario | Expected Outcome | Verification Status |
| :--- | :--- | :--- | :---: |
| `ASYNCINT-T01` | Outbox event creation | Event stored in active transaction without commit | **PASSED** |
| `ASYNCINT-T02` | Cache lifecycle & invalidation | `set_json`, `get_json`, `delete` succeed | **PASSED** |
| `ASYNCINT-T03` | Core job registry | Core handlers (`notification.send`, etc.) registered | **PASSED** |
| `ASYNCINT-T04` | Worker lifecycle startup | `WorkerSettings.on_startup` injects platform services | **PASSED** |
| `ASYNCINT-T05` | Custom task registration | Handlers can be registered dynamically at runtime | **PASSED** |

---

## 5. Verification Evidence
Verified by: `apps/api/tests/integration/test_async_infrastructure_integration.py` (all tests passing).
