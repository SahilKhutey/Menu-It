# FCD-10 — Architecture Overview & Data Flows

**Milestone:** `v1.0.0-fcd10`  
**Phase:** FCD-10 — Caching, Background Jobs & Event Infrastructure  
**Author:** AI Architecture & Core Engineering Team  
**Status:** Approved  

---

## 1. Logical Architecture

```mermaid
flowchart TD
    subgraph API_Layer["FastAPI / Domain Modules"]
        API["FastAPI Endpoints"]
        Publisher["OutboxEventPublisher"]
        JobSvc["JobService"]
    end

    subgraph Caching["Cache Subsystem"]
        CacheSvc["CacheService"]
        RedisBackend["RedisCacheBackend / InMemory"]
    end

    subgraph Durable_Storage["PostgreSQL Durable Storage"]
        OutboxDB[("event_outbox")]
        InboxDB[("processed_events")]
        JobsDB[("background_jobs")]
        DLQDB[("dead_letter_jobs")]
        SchedDB[("scheduled_jobs & runs")]
    end

    subgraph Execution_Transport["Redis Transport"]
        Broker["ARQ Redis Queue"]
        CacheStore["Redis Cache Store"]
    end

    subgraph Workers["Worker Subsystem"]
        Dispatcher["OutboxDispatcher"]
        Scheduler["JobScheduler"]
        ARQWorker["ARQ Worker Processes"]
    end

    API -->|Write Business Data + Event| OutboxDB
    API -->|Submit Job| JobsDB
    API -->|Cache Read/Write| CacheSvc
    CacheSvc --> RedisBackend --> CacheStore
    Dispatcher -->|Claim SKIP LOCKED| OutboxDB
    Dispatcher -->|Enqueue Event| Broker
    Scheduler -->|Claim Due| SchedDB
    Scheduler -->|Submit Job| JobSvc
    Broker --> ARQWorker
    ARQWorker -->|Record Deduplication| InboxDB
    ARQWorker -->|Failures| DLQDB
```

---

## 2. Reliability & Delivery Guarantees

1. **Transactional Outbox:** Business changes and event outbox rows are committed within the same PostgreSQL transaction. If the transaction rolls back, no event is ever published.
2. **At-Least-Once Delivery:** The dispatcher claims events via `FOR UPDATE SKIP LOCKED` and publishes them to workers.
3. **Idempotent Consumers:** The `processed_events` table enforces unique `(consumer_name, event_id)` insertion before running side effects.
4. **Decoupled Durability:** Redis serves as an execution transport and cache; PostgreSQL is the durable source of truth for jobs, outbox events, and dead letters.
