# FCD-14 · Document 00 — Foundation Audit & Implementation Inventory (WP-00)

## 1. Purpose & Objectives
This document records the empirical repository audit conducted prior to implementing **FCD-14 — Organization, Restaurant & Branch Management Module**. It identifies existing foundational models, services, authorization policies, routers, and migrations from FCD-01 through FCD-13 so that FCD-14 extends and integrates with them without duplicating infrastructure.

---

## 2. Existing Foundation Inventory

### 2.1 Database Models & Migrations (`apps/api/src/menu_it/database/models/` & `alembic/versions/`)
- **`Organization` (`organizations` table, `0001`–`0002`):**
  - Existing columns: `id`, `name`, `slug`, `status` (`OrganizationStatus`: `provisioning`, `active`, `suspended`, `offboarding`, `deactivated`), `created_at`, `updated_at`.
  - RLS: Enabled and forced (`organizations_tenant_isolation`).
  - **FCD-14 Action:** Extend with `legal_name`, `organization_type`, `email`, `phone`, `website`, `country_code`, `currency_code`, `timezone`, `created_by`, `updated_by`. Add `organization_settings` table.
- **`Restaurant` (`restaurants` table, `0001`–`0002`):**
  - Existing columns: `id`, `organization_id`, `name`, `slug`, `timezone`, `status` (`RestaurantStatus`: `active`, `inactive`, `suspended`, `archived`), `created_at`, `updated_at`.
  - Constraints: `uq_restaurants_organization_id_slug (organization_id, slug)`, `uq_restaurants_org_id (organization_id, id)`.
  - RLS: Enabled and forced (`restaurants_tenant_isolation`).
  - **FCD-14 Action:** Extend with `description`, `email`, `phone`, `website`, `cuisine_type`, `created_by`, `updated_by`. Add `restaurant_settings` table.
- **`OrganizationMembership` (`organization_memberships` table, `0002`–`0003`):**
  - Existing columns: `id`, `organization_id`, `user_id`, `role` (`owner`, `admin`, `manager`, `staff`, `viewer`), `status` (`invited`, `active`, `suspended`, `revoked`), `created_at`, `updated_at`.
  - **FCD-14 Action:** Extend with `joined_at`, `created_by`, `updated_by`.
- **`RestaurantMembership` (`restaurant_memberships` table, `0002`–`0003`):**
  - Existing columns: `id`, `organization_id`, `restaurant_id`, `user_id`, `role` (`manager`, `staff`, `viewer`).
  - Composite FK: `(organization_id, restaurant_id) -> restaurants(organization_id, id)`.
- **Missing Tables to Create in Migration `0009`:**
  - `branches` (with composite FK to `restaurants(organization_id, id)` and `uq_branch_org_restaurant_id`, plus RLS).
  - `branch_assignments` (with composite FK to `branches(organization_id, restaurant_id, id)`, plus RLS).
  - `organization_invitations` (token_hash, expiry, single-use status, RLS).
  - `organization_settings` & `restaurant_settings` (with RLS).

### 2.2 Authorization & Tenancy (`authorization/` & `tenancy/`)
- **`TenantContext` & `get_tenant_context`:** Authoritative server-derived tenant context resolved from user ID / Bearer JWT and active `OrganizationMembership`.
- **`Permission` & `ORGANIZATION_ROLE_PERMISSIONS` / `RESTAURANT_ROLE_PERMISSIONS`:** Already define `organization:*`, `restaurant:*`, `staff:*`.
- **FCD-14 Action:** Add `branch:read`, `branch:create`, `branch:update`, `branch:manage_assignments`, `organization:suspend`, `organization:transfer_ownership` to `Permission` and map them in `policies.py`.

### 2.3 Lifecycle & Provisioning (`services/`)
- `transition_organization()` and `transition_restaurant()` in `services/organization_lifecycle.py` and `services/restaurant_lifecycle.py` enforce FCD-04 state machines.
- `OrganizationProvisioningService` in `services/organization_provisioning.py` implements atomic organization + owner membership creation.
- **FCD-14 Action:** Reuse `transition_organization` and `transition_restaurant`; add `BranchStatus` and `transition_branch` for branch lifecycle; integrate `OutboxEventPublisher` (`menu_it.platform.events.publisher`) for durable domain events.

### 2.4 Existing API Routes (`api/v1/`)
- `organizations.py`: `GET /organizations/{organization_id}/current`, `GET /organizations/{organization_id}/access` (preserve both).
- `api/v1/modules/restaurants/router.py`: `GET /restaurants`, `GET /restaurants/{restaurant_id}`, `POST /restaurants` (preserve and extend).
- **FCD-14 Action:** Add full CRUD, settings, lifecycle, membership, invitation, and branch endpoints under `/api/v1` using FCD-07 `APIResponse` and `success_response`.

### 2.5 Existing Frontend (`apps/web`, `apps/admin`, `packages/ui`)
- Next.js 14 App Router shells with `@menu-it/ui`, `@menu-it/theme-engine`, `@menu-it/shared-types`.
- **FCD-14 Action:** Implement onboarding, organization dashboard, settings, restaurant management, branch management, membership & invitation UI in `apps/web`, and platform directory views in `apps/admin`.

---

## 3. Audit Conclusion
All foundational systems (FCD-04 tenancy/RLS, FCD-05 auth/RBAC, FCD-06 value objects, FCD-07 API envelopes, FCD-09 notifications/audit, FCD-10 outbox) are present and verified. Proceed to **WP-01 — Domain Model & Business Rules**.
