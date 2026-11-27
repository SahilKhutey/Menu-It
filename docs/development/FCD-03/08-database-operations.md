# FCD-03 — Database Operations & Maintenance Guide

## 1. Connection Pool Sizing & Capacity Planning

The maximum total connections utilized by the API instances can be calculated using:

$$C_{\text{total}} = N_{\text{workers}} \times (\text{pool\_size} + \text{max\_overflow})$$

### Default Settings
- `pool_size = 5`
- `max_overflow = 10`
- `pool_timeout = 30` (seconds)
- `pool_recycle = 1800` (seconds / 30 minutes)
- `pool_pre_ping = True` (detects stale connections before use)

With two API workers:
$$C_{\text{total}} = 2 \times (5 + 10) = 30\text{ connections}$$

Ensure the PostgreSQL `max_connections` parameter (typically 100 by default) comfortably accommodates API workers, background Celery workers, Alembic migrations, and administrative sessions.

---

## 2. Health Monitoring & Endpoints

| Endpoint | Probe Type | Behavior |
| :--- | :--- | :--- |
| `GET /api/v1/health/live` | Liveness | Checks if process is alive; returns 200 OK regardless of DB status. |
| `GET /api/v1/health/ready` | Readiness | Checks runtime readiness and database dependency when configured; returns 503 if DB is offline. |
| `GET /api/v1/database/health` | Diagnostic | Executes `SELECT 1`; returns `{"status": "healthy", "database": "reachable"}` or 503 Service Unavailable. |

---

## 3. Operational Troubleshooting Runbook

### Issue 1: PostgreSQL Offline / Connection Refused
- **Symptom:** `/api/v1/database/health` returns 503 `{"status": "unavailable", "database": "unreachable"}`.
- **Resolution:**
  1. Check container status: `docker compose ps postgres`.
  2. Inspect container logs: `docker compose logs --tail=50 postgres`.
  3. Start container: `docker compose up -d postgres`.
  4. Test connectivity: `python scripts/development/check_database.py`.

### Issue 2: Pool Exhaustion / Timeout
- **Symptom:** `TimeoutError: QueuePool limit of size 5 overflow 10 reached, connection timed out, timeout 30.00`.
- **Resolution:**
  1. Inspect long-running transactions holding connections open.
  2. Verify all endpoints use `get_db_session()` dependency to ensure connections are released.
  3. Increase `DATABASE_POOL_SIZE` or `DATABASE_MAX_OVERFLOW` in `.env`.

### Issue 3: Migration Revision Conflict
- **Symptom:** `CommandError: Target database is not up to date.`
- **Resolution:**
  1. Run `alembic current` to identify applied version.
  2. Run `alembic history` to view branch heads.
  3. Resolve merge heads or upgrade: `alembic upgrade head`.
