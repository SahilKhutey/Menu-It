# FCD-10 — Worker Configuration & Execution Framework

**Milestone:** `v1.0.0-fcd10`  
**Phase:** FCD-10 — Caching, Background Jobs & Event Infrastructure  
**Author:** AI Architecture & Core Engineering Team  
**Status:** Approved  

---

## 1. ARQ Worker Configuration

The worker process is defined in `menu_it.platform.jobs.worker.WorkerSettings`:
- **Redis Connection:** `RedisSettings.from_dsn(settings.redis_url)`.
- **Functions:** Explicitly registered handlers from `JOB_REGISTRY`.
- **Concurrency & Timeouts:** `max_jobs = 10`, `job_timeout = 300s`, `max_tries = 5`.
- **Queue Name:** `menu-it:jobs:default`.

---

## 2. Process Separation

Worker processes run independently from the FastAPI API server:
```bash
uv run arq menu_it.platform.jobs.worker.WorkerSettings
```
This guarantees that CPU-heavy tasks (e.g. image processing, report compilation, PDF generation) never starve the HTTP event loop.
