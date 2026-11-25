# FCD-10 — Database Schema & Migration Specification

**Milestone:** `v1.0.0-fcd10`  
**Phase:** FCD-10 — Caching, Background Jobs & Event Infrastructure  
**Author:** AI Architecture & Core Engineering Team  
**Status:** Approved  

---

## 1. Migration Overview

- **Revision ID:** `0007_jobs_events_schedules`
- **Revises:** `0006_files_and_notifications`
- **File:** `apps/api/alembic/versions/0007_create_fcd10_jobs_events_and_schedules.py`

---

## 2. Table Summary & RLS Policies

| Table | Purpose | RLS Policy |
| :--- | :--- | :--- |
| `background_jobs` | Tracked job status & metadata | `tenant_isolation_background_jobs` |
| `dead_letter_jobs` | Permanent & exhausted failures | `tenant_isolation_dead_letter_jobs` |
| `event_outbox` | Transactional event outbox | `tenant_isolation_event_outbox` |
| `processed_events` | Consumer inbox deduplication | Primary key `(consumer_name, event_id)` |
| `scheduled_jobs` | Schedule definitions | `tenant_isolation_scheduled_jobs` |
| `scheduled_job_runs`| Occurrence run history | Unique `run_key` |
