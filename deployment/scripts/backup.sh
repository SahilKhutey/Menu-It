#!/usr/bin/env bash
set -e

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="./backups/$TIMESTAMP"
mkdir -p "$BACKUP_DIR"

echo "=== Creating ModularMenu Snapshot Backup ($TIMESTAMP) ==="

# Dump PostgreSQL Database
docker compose exec -T postgres pg_dump -U modularmenu -d modularmenu_db > "$BACKUP_DIR/database.sql"
echo "Database dump saved to $BACKUP_DIR/database.sql"

# Archive uploads volume
docker run --rm \
  --volumes-from modularmenu_customer_api \
  -v "$(pwd)/$BACKUP_DIR":/backup \
  alpine tar czf /backup/media.tar.gz -C /app/uploads .
echo "Media storage archived to $BACKUP_DIR/media.tar.gz"

echo "=== Backup Completed Successfully ==="
