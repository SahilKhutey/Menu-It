# Runbook: Database Unavailable / Connection Exhaustion
**ModularMenu Emergency Runbook**

## 1. Symptoms
- Backend logs show `sqlalchemy.exc.OperationalError: could not connect to server`.
- `/health/ready` probe fails with HTTP 503.

## 2. Diagnostic Steps
```bash
# Check postgres container status
docker compose ps postgres

# Inspect active database connections
docker compose exec postgres psql -U menu_user -d modularmenu -c "SELECT count(*) FROM pg_stat_activity;"
```

## 3. Remediation
```bash
# Restart postgres container
docker compose restart postgres

# If pool exhausted, adjust max_connections in postgresql.conf and restart
```\n