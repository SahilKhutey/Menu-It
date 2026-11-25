# FCD-10 — Dead-Letter Queue (DLQ) Management & Replay

**Milestone:** `v1.0.0-fcd10`  
**Phase:** FCD-10 — Caching, Background Jobs & Event Infrastructure  
**Author:** AI Architecture & Core Engineering Team  
**Status:** Approved  

---

## 1. Dead-Letter Schema & Persistence

Failed jobs that exhaust retries or encounter permanent errors are recorded in `dead_letter_jobs`:
- `id`: Unique record UUID.
- `job_id`: Original job UUID.
- `organization_id`: Tenant boundary (PostgreSQL RLS enforced).
- `failure_code` & `failure_message`: Diagnostic failure information.
- `correlation_id`: Trace correlation reference.
- `replayed_at` & `replayed_by`: Audit attribution for replay operations.

---

## 2. Controlled Replay Operations

- Replay requires authorization (`POST /api/v1/internal/dead-letters/{id}/replay`).
- Validates the original job payload and tenant context.
- Generates a new job execution attempt with audit logging.
- Marks the dead-letter record as replayed with operator user ID.
