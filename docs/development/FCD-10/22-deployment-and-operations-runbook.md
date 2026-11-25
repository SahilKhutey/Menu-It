# FCD-10 — Deployment & Operations Runbook

**Milestone:** `v1.0.0-fcd10`  
**Phase:** FCD-10 — Caching, Background Jobs & Event Infrastructure  
**Author:** AI Architecture & Core Engineering Team  
**Status:** Approved  

---

## 1. Process Topologies

Production deployments operate three distinct process classes:
1. **API Web Server (FastAPI / Gunicorn / Uvicorn workers):** Handles HTTP client traffic, writes to database and event outbox.
2. **Background Job Workers (ARQ):** Subscribes to Redis job queue (`menu-it:jobs:default`), executes tasks with fresh database sessions and RLS context.
3. **Outbox & Scheduler Dispatcher:** Polling service executing `OutboxDispatcher.process_batch()` and `JobScheduler.process_due_schedules()`.

---

## 2. Dead-Letter Queue Operational Procedures

When a task enters `dead_letter_jobs`:
1. Inspect failure via `GET /api/v1/internal/dead-letters/{id}`.
2. Resolve the underlying root cause (e.g. fix third-party API credentials, network routes).
3. Trigger re-execution via `POST /api/v1/internal/dead-letters/{id}/replay`.
4. Monitor worker logs to verify successful execution and resolution.
