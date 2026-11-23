#!/usr/bin/env bash
# ModularMenu — Controlled Database Migration Runner (ARC-11 §9.4)
set -euo pipefail

echo "=== ModularMenu Database Migration Runner ==="

# Check database connectivity
python - <<'PY'
import sys, os
from sqlalchemy import create_engine, text

db_url = os.environ.get("DATABASE_URL", "postgresql+asyncpg://modularmenu:devpassword123@localhost:5432/modularmenu")
# Use sync driver for alembic migration check
sync_url = db_url.replace("+asyncpg", "").replace("+aiosqlite", "")
if "sqlite" in sync_url:
    print("Using SQLite for migration check.")
    sys.exit(0)

try:
    engine = create_engine(sync_url)
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    print("✓ Database connection verified.")
except Exception as e:
    print(f"ERROR: Cannot connect to database: {e}")
    sys.exit(1)
PY

echo "Applying Alembic migrations to head..."
(cd backend && alembic upgrade head)
echo "✓ Alembic migrations successfully applied."
