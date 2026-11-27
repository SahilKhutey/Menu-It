# FCD14-ADR-004: PostgreSQL Row-Level Security (RLS) on All FCD-14 Tables

## Status
Accepted

## Context
Application-level `WHERE organization_id = ...` filtering alone risks accidental omissions in future queries.

## Decision
Enable and force PostgreSQL RLS (`ENABLE ROW LEVEL SECURITY` + `FORCE ROW LEVEL SECURITY`) with `app.current_organization_id` policies on `branches`, `branch_assignments`, `organization_invitations`, `organization_settings`, and `restaurant_settings`.

## Consequences
- Preserves FCD-04 defense-in-depth multi-tenancy guarantees consistently across all new FCD-14 tables.
