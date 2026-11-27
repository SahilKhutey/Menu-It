# FCD-03 — Database Testing Strategy & Safeguards

## 1. Testing Strategy Overview

Database foundation verification requires tests across configuration, connection, models, constraints, repositories, atomic transactions, error handling, and migrations.

---

## 2. Test Matrix

| Category | Target Module | What is Verified |
| :--- | :--- | :--- |
| **Connection** | `test_database_connection.py` | Engine executes `SELECT 1` and returns scalar |
| **Models & Constraints** | `test_models.py` | UUID generation, timestamps, FK rejection, slug uniqueness, composite restaurant uniqueness, cascade/restrict deletion |
| **Repositories** | `test_repositories.py` | CRUD operations, slug existence, tenant-scoped queries, pagination offset/limit |
| **Transactions & Rollback** | `test_transactions.py` | Multi-repository atomic commits; deterministic rollback on constraint violation leaving zero orphaned records |
| **Migrations** | `test_migrations.py` | Alembic `upgrade head`, schema inspection, `downgrade -1`, and re-upgrade lifecycle |
| **Health Endpoints** | `test_database_health.py` | `/api/v1/database/health` (healthy vs 503 unavailable) and `/api/v1/health/ready` database check |
| **Configuration** | `test_config.py` | Default settings, custom settings, pool limits, URL parsing |

---

## 3. Test Database Protection Safeguards

To prevent catastrophic data loss during test runs, `apps/api/tests/conftest.py` implements strict safeguards:
1. **URL Validation:** If `DATABASE_TEST_URL` is set, it checks that the database name ends with `_test`. If pointed at development or production, it raises a `RuntimeError` immediately:
   ```python
   if not db_name.endswith("_test"):
     raise RuntimeError(
         "Refusing to run destructive test setup against non-test database"
     )
```
2. **In-Memory Fallback:** If `DATABASE_TEST_URL` is unset, an isolated in-memory SQLite engine with `StaticPool` is provisioned, enabling 100% test pass rate in local developer environments without external service dependencies.
3. **Foreign Key Enforcement:** SQLite connection events execute `PRAGMA foreign_keys=ON` to mirror PostgreSQL relational integrity enforcement.
