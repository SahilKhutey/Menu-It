# FCD-12 · Document 04: Database & Migration Testing

**Phase:** FCD-12 — Automated Testing & CI/CD Foundation  
**System:** Menu-It Restaurant SaaS Platform  
**Status:** Completed & Approved  
**Date:** 2026-11-26  

---

## 1. PostgreSQL Relational Integrity Testing

Menu-It uses a shared PostgreSQL database with organization-level tenant isolation. Database tests verify:
1. **Single Alembic Head:** Prevents merge conflicts in migration revisions (`alembic heads`).
2. **Fresh Schema Creation:** Validates upgrade from zero to head (`alembic upgrade head`).
3. **Row Level Security (RLS):** Validates that tenants cannot read or write data across organization boundaries.
4. **Tenant Context Cleanup:** Validates that connection pool checkout and return does not leak session variables (`app.current_organization_id`).

---

## 2. CI Database Workflow Architecture

The `.github/workflows/database-tests.yml` workflow spins up an ephemeral PostgreSQL 16 container with health checks:
```yaml
services:
  postgres:
    image: postgres:16
    env:
      POSTGRES_DB: menu_it_test
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: test_password
    ports:
      - 5432:5432
```
It runs Alembic head verification, schema migration, and integration tests before any pull request touching database models or migrations can merge.
