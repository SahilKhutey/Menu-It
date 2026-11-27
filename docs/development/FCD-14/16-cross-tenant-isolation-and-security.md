# FCD-14 — 16 Cross-Tenant Isolation & Security

## Defense-in-Depth Layers
1. **API & Authorization Layer**: Requires authenticated `AuthenticatedPrincipal`, validates organization membership, and checks granular RBAC permissions (`branch:read`, `branch:create`, `branch:update`, `branch:manage_assignments`, `organization:suspend`, `organization:transfer_ownership`).
2. **Application Service Layer**: All queries explicitly filter by `organization_id` (and `restaurant_id` for branches), raising `EntityNotFoundError` when a resource does not belong to the tenant scope.
3. **Database Relational Layer**: Composite foreign keys (`fk_branches_org_restaurant`, `fk_branch_assignments_org_branch`, `fk_restaurant_membership_org_restaurant`) prevent mismatched organization/restaurant/branch links at the schema level.
4. **PostgreSQL RLS Layer**: `ENABLE` + `FORCE ROW LEVEL SECURITY` policies enforce `app.current_organization_id` isolation on every tenant-scoped FCD-14 table.
5. **Token Security**: Invitation tokens are stored strictly as SHA-256 hashes; raw tokens are never persisted.
