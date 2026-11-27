# FCD-14 — 17 Migration & Backfill Strategy

## Forward Migration (`0009_fcd14_org_branch`)
- Extends `organizations`, `restaurants`, and `organization_memberships` with nullable/defaulted profile and audit columns so existing rows migrate without downtime.
- Creates `organization_settings`, `restaurant_settings`, `branches`, `branch_assignments`, and `organization_invitations` with composite foreign keys and RLS policies.

## Verification
- `alembic heads` resolves cleanly to `0009_fcd14_org_branch (head)`.
- `alembic upgrade head` applies cleanly in both SQLite local test environments and PostgreSQL.
- `downgrade()` cleanly drops FCD-14 tables and columns in reverse dependency order.
