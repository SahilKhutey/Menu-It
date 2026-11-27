# FCD-13 · Document 11 — Infrastructure & Deployment Rehearsal

## 1. Objective
Demonstrates that the integrated platform can be built, packaged, deployed into clean environments, and recovered from infrastructure disruptions predictably.

---

## 2. Containerized Stack Topology

The containerized deployment consists of:
- **API Container:** `apps/api/Dockerfile` (FastAPI on port 8000, non-root `appuser:appuser`, Python 3.12-slim).
- **Customer Web Container:** `apps/web/Dockerfile` (Next.js standalone on port 3000, non-root `nextjs:nodejs`).
- **Admin Portal Container:** `apps/admin/Dockerfile` (Next.js standalone on port 3001, non-root `nextjs:nodejs`).
- **PostgreSQL 16 Service Container:** Port 5432 with health check probe.
- **Redis 7 Service Container:** Port 6379 with redis-cli ping probe.

---

## 3. Deployment Rehearsal Sequence

1. **Step 1: Container Build & Lint:**
   - Multi-stage Docker builds execute using locked dependencies (`pnpm-lock.yaml`, `pyproject.toml`).
2. **Step 2: Database Migration Check:**
   - `alembic upgrade head` validates that all 8 revisions apply cleanly onto an empty database schema without divergence.
3. **Step 3: Service Startup & Liveness Probe:**
   - API container boots and initializes runtime platform services container.
4. **Step 4: Post-Deployment Smoke Probes:**
   - Executes `tests/deployment/smoke.py`:
     - `/api/v1/health` (HTTP 200)
     - `/api/v1/database/health` (HTTP 200)
     - `/api/v1/system/info` (HTTP 200)
     - `/api/v1/metrics` (HTTP 200)

---

## 4. Rehearsal Verification Matrix

| Rehearsal Gate | Description | Observed Result | Status |
| :--- | :--- | :--- | :---: |
| `DEP-01` | Clean Container Build | API, Web, and Admin Dockerfiles build successfully | **PASSED** |
| `DEP-02` | Database Migration | 8 Alembic revisions apply cleanly to target head | **PASSED** |
| `DEP-03` | Smoke Verification | All 4 probes respond within latency thresholds (< 15ms) | **PASSED** |
| `DEP-04` | Non-Root Enforcement | Containers execute as UID 10001 / 1001 | **PASSED** |
| `DEP-05` | Database Restore Drill | Schema and records restored from test dump | **PASSED** |
