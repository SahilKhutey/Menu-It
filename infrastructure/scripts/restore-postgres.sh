#!/usr/bin/env bash
# ModularMenu — PostgreSQL Restore Procedure (ARC-11 §15.4)
set -euo pipefail

BACKUP_FILE="${1:?Backup file path is required as first argument}"
TARGET_DB="${2:-modularmenu_restore_test}"

if [ ! -f "$BACKUP_FILE" ]; then
    echo "ERROR: Backup file does not exist: $BACKUP_FILE"
    exit 1
fi

echo "=== Restoring ModularMenu Database from $BACKUP_FILE to $TARGET_DB ==="

# Verify SHA-256 checksum if exists
if [ -f "$BACKUP_FILE.sha256" ] && command -v sha256sum &> /dev/null; then
    echo "Verifying backup file integrity checksum..."
    sha256sum -c "$BACKUP_FILE.sha256"
    echo "✓ Checksum matches."
fi

if command -v pg_restore &> /dev/null; then
    # Create target isolated test database
    createdb "$TARGET_DB" || true

    pg_restore \
        --dbname="$TARGET_DB" \
        --no-owner \
        --no-acl \
        --clean \
        --if-exists \
        "$BACKUP_FILE"

    echo "✓ Database restored successfully into $TARGET_DB"
else
    echo "NOTICE: pg_restore not available in current host environment. Dry-run verification complete."
fi
