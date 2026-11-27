# FCD14-ADR-001: Organization → Restaurant → Branch Hierarchy

## Status
Accepted

## Context
Menu-It must support single-location independent restaurants as well as multi-brand hospitality groups operating multiple branches per brand.

## Decision
Adopt a strict three-tier tenant hierarchy: `Organization` (billing/account tenant) → `Restaurant` (brand/operating unit) → `Branch` (physical/operational location), with `organization_id` carried on every child entity.

## Consequences
- Enables unified tenant isolation via `organization_id` at every level.
- Allows a single organization to manage multiple restaurant brands and branches without duplicating user accounts.
