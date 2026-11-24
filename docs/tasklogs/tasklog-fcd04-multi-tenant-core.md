# Tasklog: FCD-04 Multi-Tenant Core Foundation

**Date:** 2026-11-24  
**Task:** Implementation, Verification, Documentation, and Release of FCD-04  
**Status:** Completed  
**Milestone:** `v1.0.0-fcd04`  
**Phase:** Foundational Core Development (FCD-04)  

---

## Task Execution Breakdown

- [x] **WP-01: Canonical Organization Ownership Foundation**
  - Reconciled FCD-03 `tenants` into canonical `organizations` and `restaurants.tenant_id` into `restaurants.organization_id`.
  - Created `apps/api/src/menu_it/database/models/organization.py` with `Organization`, `OrganizationStatus` (`PROVISIONING`, `ACTIVE`, `SUSPENDED`, `OFFBOARDING`, `DEACTIVATED`).
  - Added backward-compatible aliases `Tenant = Organization` and `TenantStatus = OrganizationStatus` in `database/models/tenant.py`.
  - Authored Alembic migration `apps/api/alembic/versions/0002_establish_organization_tenant_foundation.py` with table renames, column alters, constraint updates, and RLS policies.

- [x] **WP-02: Membership and Assignment Schemas**
  - Created `apps/api/src/menu_it/database/models/organization_membership.py` (`OrganizationMembership`, `OrganizationRole`, `MembershipStatus`, unique `(organization_id, user_id)`).
  - Updated `apps/api/src/menu_it/database/models/restaurant.py` with `organization_id`, composite constraints `uq_restaurants_organization_id_slug`, `uq_restaurants_org_id`, and `RestaurantStatus` (`ACTIVE`, `INACTIVE`, `SUSPENDED`, `ARCHIVED`).
  - Added compatibility synonym `tenant_id = synonym("organization_id")` on `Restaurant`.
  - Created `apps/api/src/menu_it/database/models/restaurant_membership.py` (`RestaurantMembership`, `RestaurantRole`, composite FK `(organization_id, restaurant_id) -> restaurants(organization_id, id)`).
  - Created `apps/api/src/menu_it/database/models/audit.py` (`OrganizationAuditEvent` with JSONB metadata and indexing).
  - Updated `apps/api/src/menu_it/database/models/__init__.py` to export all models.

- [x] **WP-03: Immutable TenantContext**
  - Created `apps/api/src/menu_it/tenancy/context.py` (`TenantContext` frozen slots dataclass, `SystemTenantContext`).
  - Created `apps/api/src/menu_it/tenancy/contextvar.py` (`set_current_tenant`, `get_current_tenant`, `reset_current_tenant`).

- [x] **WP-04: Tenant Identification & Resolution**
  - Created `apps/api/src/menu_it/auth/principal.py` (`AuthenticatedPrincipal(user_id, is_authenticated)`).
  - Created `apps/api/src/menu_it/tenancy/exceptions.py` (`TenantResolutionError`, `TenantNotFoundError`, `TenantAccessDeniedError`, `TenantSuspendedError`, `RestaurantAccessDeniedError`, `TenantContextMissingError`).
  - Created `apps/api/src/menu_it/tenancy/resolver.py` (`TenantResolver` validating identity, membership, lifecycle status, and restaurant assignments; owner/admin implied restaurant access).

- [x] **WP-05: Tenant-Aware API Dependencies**
  - Created `apps/api/src/menu_it/auth/dependencies.py` (`get_current_principal` validating `X-User-ID`).
  - Created `apps/api/src/menu_it/tenancy/dependencies.py` (`get_tenant_context`, `get_restaurant_tenant_context`).
  - Created `apps/api/src/menu_it/api/v1/endpoints/organizations.py` (`GET /api/v1/organizations/{organization_id}/current`).
  - Registered `organizations.router` in `apps/api/src/menu_it/api/v1/router.py`.

- [x] **WP-06: Tenant-Scoped Repository Layer**
  - Created `apps/api/src/menu_it/repositories/tenant_base.py` (`TenantScopedRepository[ModelType]` enforcing `model.organization_id == self.context.organization_id`).
  - Created `apps/api/src/menu_it/repositories/tenant_restaurants.py` (`TenantRestaurantRepository`).
  - Updated `apps/api/src/menu_it/repositories/__init__.py`.

- [x] **WP-07 & WP-08: RLS & Transaction Integration**
  - Created `apps/api/src/menu_it/database/tenant_scope.py` (`set_database_tenant_context` with transaction-local `set_config('app.current_organization_id', ..., true)`).
  - Created `apps/api/src/menu_it/database/unit_of_work.py` (`tenant_transaction`, `TenantUnitOfWork`).

- [x] **WP-09 & WP-10: Lifecycle State Machines**
  - Created `apps/api/src/menu_it/services/organization_lifecycle.py` (`ALLOWED_TRANSITIONS`, `transition_organization`, `InvalidOrganizationTransition`).
  - Created `apps/api/src/menu_it/services/restaurant_lifecycle.py` (`ALLOWED_RESTAURANT_TRANSITIONS`, `transition_restaurant`, `InvalidRestaurantTransition`).

- [x] **WP-11: Provisioning & Offboarding Primitives**
  - Created `apps/api/src/menu_it/services/organization_provisioning.py` (`OrganizationProvisioningService.provision_organization` creating Org in PROVISIONING, Owner Membership, initial Restaurant, Audit Event, and transitioning to ACTIVE atomically).
  - Updated `apps/api/src/menu_it/services/__init__.py`.

- [x] **WP-12: Tenant-Aware Infrastructure Interfaces**
  - Created `apps/api/src/menu_it/tenancy/infrastructure.py` (`TenantJobContext`, `format_tenant_storage_key`, `format_tenant_cache_key`, `record_audit_event`).
  - Updated `apps/api/src/menu_it/tenancy/__init__.py`.

- [x] **WP-13: Security & Test Suites**
  - Authored `apps/api/tests/unit/test_tenant_context.py`
  - Authored `apps/api/tests/unit/test_organization_lifecycle.py`
  - Authored `apps/api/tests/unit/test_restaurant_lifecycle.py`
  - Authored `apps/api/tests/integration/test_tenant_resolver.py`
  - Authored `apps/api/tests/integration/test_tenant_repositories.py`
  - Authored `apps/api/tests/integration/test_organization_provisioning.py`
  - Authored `apps/api/tests/security/test_rls_isolation.py`
  - Authored `apps/api/tests/security/test_api_tenant_security.py`
  - Updated `apps/api/tests/integration/test_migrations.py` to verify full upgrade/downgrade through `0002_org_foundation`.
  - Updated `apps/api/tests/integration/test_models.py` for `TenantStatus.ACTIVE`.
  - Executed pytest suite: 72 passed out of 72 tests (100% pass rate) with 92% coverage.

- [x] **WP-14: Documentation & Release Artifacts**
  - Created 15 comprehensive technical documents in `docs/development/FCD-04/`.
  - Created `docs/devlogs/devlog-018-fcd04-multi-tenant-core-foundation.md`.
  - Created `docs/tasklogs/tasklog-fcd04-multi-tenant-core.md`.
  - Updated index README files in `docs/devlogs/` and `docs/tasklogs/`.
