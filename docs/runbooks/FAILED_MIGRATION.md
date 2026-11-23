# Runbook: Failed Database Migration
**ModularMenu Emergency Runbook**

## 1. Symptoms
- `alembic upgrade head` fails with SQL syntax error or lock timeout.

## 2. Remediation
```bash
# 1. Identify failing revision
docker compose exec backend alembic current

# 2. Revert to previous safe migration revision
docker compose exec backend alembic downgrade -1

# 3. If database state corrupted, restore pre-migration backup
bash infrastructure/scripts/restore-postgres.sh /var/backups/modularmenu/pre_migration_backup.sql.gz
```\n