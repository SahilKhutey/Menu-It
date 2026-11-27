# FCD-04 — Database Migrations & Schema Evolution

## 1. Migration Overview

Phase FCD-04 introduces revision `0002_establish_organization_tenant_foundation.py` to upgrade the initial FCD-03 database schema to the canonical ARC-05 multi-tenant model.

### Migration Metadata
- **Revision ID**: `0002_org_foundation`
- **Revises**: `0001_initial_tables`
- **Direction**: Forward (upgrade) and Reversible (downgrade)
- **Verified Compatibility**: PostgreSQL 17 and SQLite (via conditional dialect branching)

---

## 2. Upgrade Actions

1. **Table Rename**:
   ```sql
   ALTER TABLE tenants RENAME TO organizations;
   ALTER TABLE organizations RENAME CONSTRAINT uq_tenants_slug TO uq_organizations_slug;
   ```
2. **Column Rename & Foreign Key**:
   ```sql
   ALTER TABLE restaurants RENAME COLUMN tenant_id TO organization_id;
   ALTER TABLE restaurants DROP CONSTRAINT fk_restaurants_tenant_id_tenants;
   ALTER TABLE restaurants ADD CONSTRAINT fk_restaurants_organization_id_organizations
       FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE RESTRICT;
   ```
3. **Composite Unique Constraints**:
   - `uq_restaurants_organization_id_slug` on `restaurants(organization_id, slug)`
   - `uq_restaurants_org_id` on `restaurants(organization_id, id)` for composite foreign keys
4. **New Tables**:
   - `organization_memberships` (with unique `(organization_id, user_id)`)
   - `restaurant_memberships` (with composite FK to `restaurants(organization_id, id)`)
   - `organization_audit_events` (JSONB audit trail)
5. **Row-Level Security Policies**:
   - Enables and forces RLS on `restaurants`, `organization_memberships`, `restaurant_memberships`, `organization_audit_events` using `NULLIF(current_setting('app.current_organization_id', true), '')::uuid`.

---

## 3. Reversibility & Downgrade Actions

The migration includes a complete, deterministic downgrade path:
1. Drops RLS policies on PostgreSQL.
2. Drops `organization_audit_events`, `restaurant_memberships`, and `organization_memberships`.
3. Restores composite constraints on `restaurants`.
4. Restores foreign key and renames `organization_id` back to `tenant_id`.
5. Renames `organizations` back to `tenants`.

Verified end-to-end via automated migration test `test_alembic_migration_lifecycle`.
