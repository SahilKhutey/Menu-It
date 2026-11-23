# Database Operations Guide
**ModularMenu Operational Documentation**

## 1. PostgreSQL Maintenance
```bash
# Connect to PostgreSQL shell
docker compose exec postgres psql -U menu_user -d modularmenu

# Inspect active database connections
SELECT count(*), state FROM pg_stat_activity GROUP BY state;

# Inspect table bloat and vacuum stats
SELECT relname, last_vacuum, last_autovacuum FROM pg_stat_user_tables;

# Run manual vacuum analyze
docker compose exec postgres vacuumdb -U menu_user -d modularmenu --analyze
```

## 2. Row-Level Security Verification
Verify tenant isolation is operating as expected:
```sql
SET LOCAL app.current_org_id = '00000000-0000-0000-0000-000000000001';
SELECT count(*) FROM restaurants; -- Returns strictly org 1 rows
```\n