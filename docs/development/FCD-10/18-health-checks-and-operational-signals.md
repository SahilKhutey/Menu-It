# FCD-10 — Health Checks & Operational Signals

**Milestone:** `v1.0.0-fcd10`  
**Phase:** FCD-10 — Caching, Background Jobs & Event Infrastructure  
**Author:** AI Architecture & Core Engineering Team  
**Status:** Approved  

---

## 1. Health Endpoints Inventory

- `GET /api/v1/health/live`: Basic process liveness probe.
- `GET /api/v1/health/ready`: Application readiness verifying runtime initialization and optional DB ping.
- `GET /api/v1/health/platform`: Component-level health reporting `database`, `storage`, `notifications`, `redis`, and `jobs`.

---

## 2. Operational Signals

- **Queue Depth:** Total jobs queued in Redis/ARQ.
- **Outbox Backlog:** Count of rows in `event_outbox` where `published_at IS NULL`.
- **Dead-Letter Backlog:** Count of un-replayed rows in `dead_letter_jobs`.
- **Worker Heartbeat:** Recent timestamp confirming worker process responsiveness.
