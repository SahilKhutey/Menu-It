# FCD14-ADR-003: Composite Foreign Keys for Tenant Integrity

## Status
Accepted

## Context
Child entities (`branches`, `branch_assignments`, `restaurant_memberships`) reference both `organization_id` and a parent entity ID (`restaurant_id` or `branch_id`).

## Decision
Enforce composite foreign keys (`(organization_id, restaurant_id)` → `restaurants(organization_id, id)` and `(organization_id, branch_id)` → `branches(organization_id, id)`) in PostgreSQL and SQLAlchemy models.

## Consequences
- Makes cross-organization parent-child linking structurally impossible at the database constraint level.
