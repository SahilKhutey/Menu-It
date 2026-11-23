# Database Restore Procedure
**ModularMenu Operational Documentation**

## 1. Restore Execution
Execute `infrastructure/scripts/restore-postgres.sh`:
```bash
bash infrastructure/scripts/restore-postgres.sh /var/backups/modularmenu/modularmenu_20261123_020000.sql.gz
```

## 2. Verification Steps Post-Restore
1. Confirm schema version: `alembic current`.
2. Verify row counts and tenant integrity.
3. Validate API readiness: `curl -s http://localhost:8000/health/ready`.\n