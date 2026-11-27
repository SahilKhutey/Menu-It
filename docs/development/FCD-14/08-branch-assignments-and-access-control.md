# FCD-14 — 08 Branch Assignments & Access Control

## Branch Assignments
`BranchManagementService` provides `list_assignments`, `upsert_assignment`, and `remove_assignment` backed by `BranchAssignment` (`branch_assignments` table).

## Invariants & Authorization
- **Same-Organization Scope**: `ensure_same_organization_scope` ensures only users with an active `OrganizationMembership` in the target `organization_id` can be assigned to a branch.
- **Branch Roles**: Supports `BranchRole` values (`manager`, `supervisor`, `staff`, `viewer`).
- **RBAC Permissions**: Extended `apps/api/src/menu_it/authorization/{permissions.py,policies.py}` with:
  - `branch:read`
  - `branch:create`
  - `branch:update`
  - `branch:manage_assignments`
  - `organization:suspend`
  - `organization:transfer_ownership`
