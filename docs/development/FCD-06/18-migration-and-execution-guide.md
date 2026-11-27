# FCD-06 §18 — Migration & Execution Guide

## 1. Migration Specification

Migration `0004_create_restaurant_profiles.py`:
- Revision ID: `0004_restaurant_profiles`
- Down Revision: `0003_identity_foundation`
- Creates table `restaurant_profiles` with primary key, foreign keys, unique constraint on `restaurant_id`, and indexes on `organization_id` and `restaurant_id`.
- Applies composite foreign key `fk_restaurant_profiles_org_restaurant` pointing to `restaurants(organization_id, id)`.
- Conditionally creates PostgreSQL RLS policy `restaurant_profiles_tenant_isolation`.

## 2. Execution Commands

### 2.1 Upgrade to Latest
```bash
cd apps/api
alembic upgrade head
```

### 2.2 Downgrade Revision
```bash
cd apps/api
alembic downgrade -1
```

### 2.3 Automated Lifecycle Test
```bash
python -m pytest apps/api/tests/integration/test_migrations.py -v
```
Verifies full upgrade/downgrade sequence:
`0001 -> 0004 -> 0003 -> 0002 -> 0001 -> base -> 0004`.
All steps successfully passed.
