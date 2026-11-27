# FCD-04 — Multi-Tenant Security & Isolation Testing

## 1. Security Testing Strategy

Menu-It treats multi-tenant boundaries as critical security perimeters. Verification requires testing negative cases (attack scenarios) with equal rigor to positive cases.

### Test Categories
1. **RLS Isolation Tests** (`tests/security/test_rls_isolation.py`):
   - Verifies `set_database_tenant_context` correctly sets `app.current_organization_id` inside PostgreSQL transactions.
   - Verifies unit of work resets state between transactions.
2. **API Boundary Tests** (`tests/security/test_api_tenant_security.py`):
   - Missing authentication header rejected with HTTP 401.
   - Malformed user ID format rejected with HTTP 401.
   - User without membership in organization rejected with HTTP 404 (preventing organization enumeration).
   - Member of suspended organization rejected with HTTP 403 Forbidden.
   - Authorized member successfully resolves context with HTTP 200.
3. **Repository Cross-Tenant Tests** (`tests/integration/test_tenant_repositories.py`):
   - Organization A cannot read Organization B's restaurants via `get_by_id`.
   - Organization A `list()` returns only Organization A records.
   - Cross-tenant update attempts return `None` and do not alter target records.
   - Cross-tenant delete attempts return `False` and do not delete target records.
   - `create()` automatically overwrites entity `organization_id` with active context ID.
4. **Resolver Trust Tests** (`tests/integration/test_tenant_resolver.py`):
   - Unauthenticated principal raises `TenantAccessDeniedError`.
   - Non-existent organization raises `TenantNotFoundError`.
   - Non-member user raises `TenantNotFoundError`.
   - Pending, suspended, and revoked memberships raise `TenantAccessDeniedError`.
   - Suspended and offboarding organizations raise `TenantSuspendedError`.
   - Cross-organization restaurant access raises `RestaurantAccessDeniedError`.
   - Inactive restaurant raises `RestaurantAccessDeniedError`.

---

## 2. Test Execution Summary

All 72 tests across unit, integration, and security suites pass with zero failures:

```
apps/api/tests/security/test_api_tenant_security.py::test_endpoint_requires_authentication PASSED
apps/api/tests/security/test_api_tenant_security.py::test_endpoint_rejects_malformed_user_id PASSED
apps/api/tests/security/test_api_tenant_security.py::test_endpoint_unrelated_user_returns_404 PASSED
apps/api/tests/security/test_api_tenant_security.py::test_endpoint_suspended_org_returns_403 PASSED
apps/api/tests/security/test_api_tenant_security.py::test_endpoint_authorized_member_returns_context PASSED
apps/api/tests/security/test_rls_isolation.py::test_tenant_transaction_context_lifecycle PASSED
apps/api/tests/security/test_rls_isolation.py::test_tenant_unit_of_work PASSED
apps/api/tests/security/test_rls_isolation.py::test_set_database_tenant_context_postgres_dialect PASSED
apps/api/tests/integration/test_tenant_repositories.py::test_tenant_a_cannot_read_tenant_b_restaurant PASSED
apps/api/tests/integration/test_tenant_repositories.py::test_tenant_a_lists_only_own_restaurants PASSED
apps/api/tests/integration/test_tenant_repositories.py::test_tenant_cross_mutation_rejected PASSED
apps/api/tests/integration/test_tenant_repositories.py::test_create_automatically_assigns_tenant_id PASSED
apps/api/tests/integration/test_tenant_resolver.py::test_user_cannot_resolve_unrelated_organization PASSED
apps/api/tests/integration/test_tenant_resolver.py::test_active_member_resolves_organization PASSED
apps/api/tests/integration/test_tenant_resolver.py::test_membership_statuses_rejected PASSED
apps/api/tests/integration/test_tenant_resolver.py::test_organization_statuses_enforced PASSED
apps/api/tests/integration/test_tenant_resolver.py::test_restaurant_resolution_and_scope PASSED
```
