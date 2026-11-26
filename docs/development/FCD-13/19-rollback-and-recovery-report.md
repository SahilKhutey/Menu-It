# FCD-13 · Document 19 — Rollback & Recovery Report

## 1. Objective
Specifies the operational procedures and recovery steps to execute in the event of an infrastructure failure, failed deployment, or database disruption during release operations.

---

## 2. Rollback Decision Triggers
A rollback must be initiated immediately if any of the following occur during or immediately following deployment:
1. **Critical Smoke Probe Failure:** Post-deployment smoke probes (`tests/deployment/smoke.py`) fail repeatedly after service container startup.
2. **Elevated HTTP 5xx Error Rate:** Error rate exceeds 0.5% over a 5-minute rolling window.
3. **Database Migration Failure:** `alembic upgrade head` aborts with an unrecoverable SQL error.
4. **Data Leakage or Boundary Breach:** Any cross-tenant authorization violation detected in security logs.

---

## 3. Rollback Runbook Procedures

### Procedure A: Application Container Rollback (Zero Schema Impact)
If database migrations have not been applied or the schema changes are strictly backward-compatible:
```powershell
# 1. Revert reverse proxy / load balancer traffic to the previous healthy container image
# 2. Redeploy previous approved stable image tags
docker compose -f docker-compose.prod.yml up -d --no-deps api web admin

# 3. Execute smoke verification against previous containers
python tests/deployment/smoke.py
```

### Procedure B: Database Schema Rollback (Single Revision Downgrade)
If a newly applied Alembic revision must be reversed:
```powershell
# 1. Stop incoming API traffic (drain connections)
# 2. Downgrade single migration revision
cd apps/api
alembic downgrade -1

# 3. Verify current revision
alembic current
```

### Procedure C: Full Disaster Recovery from PostgreSQL Backup
In the event of catastrophic data corruption:
```powershell
# 1. Terminate all active backend connections
# 2. Restore PostgreSQL dump into isolated database
pg_restore --clean --if-exists --no-owner --dbname=$env:DATABASE_URL menu_it_backup.dump

# 3. Verify schema revision and referential integrity
alembic current

# 4. Run post-restore tenant isolation verification
python -m pytest apps/api/tests/security/test_tenant_isolation_assurance.py -v
```

---

## 4. Recovery Testing Verification
- Database rollback procedures and isolated dump restoration verified in testing environment drills.
- RLS tenant boundaries remain strictly enforced post-restoration.
