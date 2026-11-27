# FCD-10 — Scheduling & Recurring Jobs Infrastructure

**Milestone:** `v1.0.0-fcd10`  
**Phase:** FCD-10 — Caching, Background Jobs & Event Infrastructure  
**Author:** AI Architecture & Core Engineering Team  
**Status:** Approved  

---

## 1. Persistent Database-Backed Schedules

Schedule definitions are persisted in PostgreSQL in the `scheduled_jobs` table:
- `schedule_type`: `"interval"` (e.g. `15m`, `1h`), `"daily"` (e.g. `04:00`), or `"once"`.
- `timezone`: IANA timezone string (e.g. `Asia/Kolkata`, `UTC`).
- `next_run_at`: UTC instant of the next scheduled execution.
- `enabled`: Boolean toggle.

---

## 2. Occurrence Tracking & Deduplication

The `scheduled_job_runs` table tracks every execution occurrence:
- Unique `run_key = f"{schedule_id}:{scheduled_for.isoformat()}"`.
- Guarantees that multiple competing schedulers or restarts never execute the same calendar slot more than once.
