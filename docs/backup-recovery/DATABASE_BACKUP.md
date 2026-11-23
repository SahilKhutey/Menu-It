# Database Backup Procedure
**ModularMenu Operational Documentation**

## 1. Automated Backup Script
Execute the standardized backup script (`infrastructure/scripts/backup-postgres.sh`):
```bash
bash infrastructure/scripts/backup-postgres.sh
```

## 2. Manual Backup Execution
```bash
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="/var/backups/modularmenu/modularmenu_${TIMESTAMP}.sql.gz"

docker compose exec -T postgres pg_dump -U menu_user -d modularmenu | gzip > "${BACKUP_FILE}"
sha256sum "${BACKUP_FILE}" > "${BACKUP_FILE}.sha256"
```\n