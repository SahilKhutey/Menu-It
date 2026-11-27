# FCD14-ADR-009: Granular Branch & Organization RBAC Permissions

## Status
Accepted

## Context
Existing FCD-05 permissions covered organization and restaurant scopes but lacked branch-level and ownership-transfer granularity.

## Decision
Extend `authorization/permissions.py` and `authorization/policies.py` with `branch:read`, `branch:create`, `branch:update`, `branch:manage_assignments`, `organization:suspend`, and `organization:transfer_ownership`.

## Consequences
- Allows fine-grained authorization checks for branch managers without granting full organization-wide ownership privileges.
