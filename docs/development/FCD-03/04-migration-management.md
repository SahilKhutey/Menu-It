# FCD-03 — Alembic Migration Management & Policy

## 1. Alembic Setup & Infrastructure

Alembic provides version-controlled schema evolution for Menu-It. Configuration resides in:
- `apps/api/alembic.ini`: Configuration, sys.path prepending, logging directives.
- `apps/api/alembic/env.py`: Asynchronous engine connection runner, offline SQL generator, metadata provider.
- `apps/api/alembic/script.py.mako`: Template for generated migrations.
- `apps/api/alembic/versions/`: Versioned migration scripts.

---

## 2. Standard Migration Commands

| Operation | Command | Description |
| :--- | :--- | :--- |
| **Generate Revision** | `alembic revision --autogenerate -m "description"` | Generates a new migration by diffing models against DB |
| **Apply All Pending** | `alembic upgrade head` | Migrates to the latest revision |
| **Apply One Step** | `alembic upgrade +1` | Increments schema by one revision |
| **Rollback One Step** | `alembic downgrade -1` | Rolls back the most recent revision |
| **Check Current Version** | `alembic current` | Prints current applied migration hash |
| **Inspect History** | `alembic history` | Shows complete chronological migration log |
| **Offline SQL Preview** | `alembic upgrade head --sql` | Prints the static transactional DDL script |

---

## 3. Initial Migration (`0001_initial_tables`)

The initial migration establishes:
- `tenants` table with unique constraint and index on `slug`.
- `restaurants` table with composite unique constraint `uq_restaurants_tenant_id_slug`.
- Foreign key `fk_restaurants_tenant_id_tenants` ondelete RESTRICT.
- `alembic_version` tracking table.

### Downgrade Verification
Downgrade safely reverses the operations in reverse dependency order:
1. Drop index `ix_restaurants_tenant_id`
2. Drop table `restaurants`
3. Drop index `ix_tenants_slug`
4. Drop table `tenants`

---

## 4. Migration Policy & Production Safeguards

1. **Model First:** Always update the SQLAlchemy model before generating migrations.
2. **Review Generated DDL:** Inspect generated operations; autogenerate cannot detect column renames or complex constraint nuances.
3. **Expand & Contract:** In production, avoid breaking migrations that drop active columns. Use multi-stage backward-compatible deployments.
4. **Automated Verification:** Every migration must pass automated lifecycle tests (`upgrade head -> downgrade -1 -> upgrade head`).
