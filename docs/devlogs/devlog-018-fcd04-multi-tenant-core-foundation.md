# Devlog 018 — FCD-04 Multi-Tenant Core Foundation

**Date:** 2026-11-24  
**Author:** AI Architecture & Core Engineering Team  
**Subject:** Implementation, Verification, and Release of FCD-04 Multi-Tenant Core Foundation  
**Milestone:** `v1.0.0-fcd04`  
**Phase:** Foundational Core Development (FCD-04)  
**Parent Documents:** FCD-01, FCD-02, FCD-03, ARC-01 through ARC-12  

---

## 1. Objectives & Context

Phase **FCD-04** establishes the canonical multi-tenant architecture for the **Menu-It** restaurant SaaS platform. It converts the baseline persistent data layer from FCD-03 into a secure, isolated, multi-tenant system with:
1. **Canonical Organization Entity & Reconciliation:** Reconciled earlier FCD-03 naming (`tenants` -> `organizations`, `restaurants.tenant_id` -> `restaurants.organization_id`) in accordance with ARC-05 architecture, preserving backward compatibility.
2. **Membership & Assignment Models:** `organization_memberships` (`owner`, `admin`, `member`, `billing_admin`) and `restaurant_memberships` (`manager`, `staff`) with composite foreign key integrity `(organization_id, restaurant_id) -> restaurants(organization_id, id)`.
3. **Immutable TenantContext:** Frozen, slotted `TenantContext` containing `organization_id`, `user_id`, `organization_role`, optional restaurant scoping, and correlation tracking.
4. **Trusted Tenant Resolution:** Rejection of all untrusted client tenant headers; server-side resolution via `TenantResolver` verifying principal identity, organization active status, and active user membership.
5. **FastAPI Dependency Injection:** `get_tenant_context` and `get_restaurant_tenant_context` dependencies, with `/api/v1/organizations/{organization_id}/current` endpoint.
6. **Defense-in-Depth Isolation:**
   - **Repository Layer:** `TenantScopedRepository[ModelType]` automatically scoping queries and inserts with `organization_id`.
   - **Database Layer:** PostgreSQL Row-Level Security (RLS) policies on `restaurants`, `organization_memberships`, `restaurant_memberships`, and `organization_audit_events`.
   - **Connection Pool Safety:** Transaction-local `set_config('app.current_organization_id', ..., true)` eliminating cross-request pool contamination.
7. **Lifecycle State Machines:** Deterministic transition matrices for `OrganizationStatus` (`PROVISIONING`, `ACTIVE`, `SUSPENDED`, `OFFBOARDING`, `DEACTIVATED`) and `RestaurantStatus` (`ACTIVE`, `INACTIVE`, `SUSPENDED`, `ARCHIVED`).
8. **Atomic Provisioning Service:** `OrganizationProvisioningService` coordinating multi-table onboarding, initial restaurant assignment, and audit events within an atomic transaction.
9. **Tenant-Aware Infrastructure:** Namespaced object storage keys (`org_{id}/...`), Redis cache keys (`org:{id}:...`), background job context (`TenantJobContext`), and audit logging (`OrganizationAuditEvent`).
10. **Comprehensive Verification:** 72 unit, integration, and security tests passing with 92% coverage, zero linter errors, and 15 technical documents.

---

## 2. Key Engineering Accomplishments

### 2.1 Schema Reconciliation & Alembic Migration (WP-01, WP-02)
- Created `apps/api/alembic/versions/0002_establish_organization_tenant_foundation.py` performing table renames, column alters, constraint creations, and RLS policy provisioning.
- Implemented `Organization` and `OrganizationStatus` in `database/models/organization.py`, with backward compatibility alias `Tenant = Organization`.
- Implemented `OrganizationMembership`, `OrganizationRole`, and `MembershipStatus` in `database/models/organization_membership.py`.
- Updated `Restaurant` model in `database/models/restaurant.py` with `organization_id`, composite constraints, `RestaurantStatus`, and compatibility synonym `tenant_id = synonym("organization_id")`.
- Implemented `RestaurantMembership` in `database/models/restaurant_membership.py` enforcing composite FK `(organization_id, restaurant_id)`.
- Implemented `OrganizationAuditEvent` in `database/models/audit.py` with JSONB audit payload and composite indexing.

### 2.2 Context & Resolution Pipeline (WP-03 – WP-05)
- Created frozen, slotted dataclass `TenantContext` in `tenancy/context.py` and `SystemTenantContext` for async tasks.
- Implemented async-safe `ContextVar` management in `tenancy/contextvar.py` (`set_current_tenant`, `get_current_tenant`, `reset_current_tenant`).
- Defined `AuthenticatedPrincipal` in `auth/principal.py` and extraction dependency `get_current_principal` in `auth/dependencies.py`.
- Implemented `TenantResolver` in `tenancy/resolver.py`, enforcing active organization status, active user membership, and restaurant assignment checks.
- Created FastAPI dependencies in `tenancy/dependencies.py` and endpoint `GET /api/v1/organizations/{organization_id}/current`.

### 2.3 Repository Scoping & RLS Isolation (WP-06 – WP-08)
- Created `TenantScopedRepository[ModelType]` in `repositories/tenant_base.py` automatically filtering queries by `organization_id` and injecting it on creation.
- Implemented `TenantRestaurantRepository` in `repositories/tenant_restaurants.py`.
- Created `set_database_tenant_context` in `database/tenant_scope.py` setting `set_config('app.current_organization_id', :org_id, true)`.
- Created `tenant_transaction` context manager and `TenantUnitOfWork` in `database/unit_of_work.py`.

### 2.4 State Machines & Provisioning (WP-09 – WP-11)
- Implemented `OrganizationLifecycleService` (`services/organization_lifecycle.py`) and `RestaurantLifecycleService` (`services/restaurant_lifecycle.py`) with transition validation.
- Implemented `OrganizationProvisioningService` in `services/organization_provisioning.py` executing atomic onboarding workflows.

### 2.5 Infrastructure Interfaces & Audit (WP-12)
- Created helper utilities in `tenancy/infrastructure.py` for storage paths, cache keys, audit records, and `TenantJobContext`.

---

## 3. Verification & Metrics

- **Backend Pytest Suite:** 72 passed out of 72 tests (100% pass rate) in 2.15 seconds.
- **Backend Test Coverage:** 92% across all modules (829 statements, 63 missed).
- **Backend Ruff Lint:** 0 errors across 88 files.
- **Backend Ruff Format:** 100% compliant.
- **Frontend TypeScript:** 3/3 packages clean (web, admin, shared-types).
- **Frontend ESLint:** 0 errors / 0 warnings.
- **Prettier:** All workspace files formatted.

---

## 4. Next Steps
With the multi-tenant core foundation established and verified, Menu-It is primed for **FCD-05 — Authentication, User Identity & Access Management**.
