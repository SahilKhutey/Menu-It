# FCD-14 — 03 Database Schema & Row-Level Security

## Migration
Alembic migration `0009_create_fcd14_org_restaurant_branch_tables.py` (revises `0008_security_audit_events`, head `0009_fcd14_org_branch`) introduces and extends the FCD-14 relational schema.

## Tables Added & Extended
- **`organizations` & `restaurants` & `organization_memberships` (extended)**: Added profile, contact, regional, and audit columns (`created_by`, `updated_by`).
- **`organization_settings` & `restaurant_settings`**: Dedicated 1:1 settings tables keyed by `organization_id` / `restaurant_id`.
- **`branches`**: Belongs to `(organization_id, restaurant_id)` via composite foreign key `fk_branches_org_restaurant` referencing `restaurants(organization_id, id)`.
- **`branch_assignments`**: Links `(organization_id, branch_id)` and `user_id` with `BranchRole` (`manager`, `supervisor`, `staff`, `viewer`).
- **`organization_invitations`**: Stores `token_hash` (SHA-256), `email`, `role`, `status`, `expires_at`, and audit metadata.

## PostgreSQL RLS Enforcement
All tenant-scoped FCD-14 tables (`branches`, `branch_assignments`, `organization_invitations`, `organization_settings`, `restaurant_settings`) have `ENABLE ROW LEVEL SECURITY`, `FORCE ROW LEVEL SECURITY`, and tenant isolation `CREATE POLICY` statements binding queries to `current_setting('app.current_organization_id', true)`.
