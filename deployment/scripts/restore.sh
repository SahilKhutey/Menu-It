#!/usr/bin/env bash
set -e

if [ -z "$1" ]; then
    echo "Usage: ./restore.sh <backup_folder_path>"
    exit 1
fi

BACKUP_DIR="$1"

if [ ! -f "$BACKUP_DIR/database.sql" ]; then
    echo "Error: $BACKUP_DIR/database.sql not found."
    exit 1
fi

echo "=== Restoring ModularMenu from $BACKUP_DIR ==="

# Restore Database
docker compose exec -T postgres psql -U modularmenu -d modularmenu_db < "$BACKUP_DIR/database.sql"
echo "Database restored."

# Restore Media Archive
if [ -f "$BACKUP_DIR/media.tar.gz" ]; then
    docker run --rm \
      --volumes-from modularmenu_customer_api \
      -v "$(pwd)/$BACKUP_DIR":/backup \
      alpine tar xzf /backup/media.tar.gz -C /app/uploads
    echo "Media files restored."
fi

echo "=== Restoration Complete! ==="
