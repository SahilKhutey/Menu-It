# Devlog-028: FCD-14 Organization, Restaurant & Branch Management Module

**Date:** 2026-11-27  
**Milestone / Tag:** `FCD-14` / `v0.2.0-fcd14`  
**Status:** Implemented & Verified  

---

## 1. Objective
Convert the foundational platform (FCD-01–FCD-13) into Menu-It's first major business-facing module:
- **Organization onboarding & management** (tenant accounts, settings, suspension, ownership transfer).
- **Restaurant management** (brands under an organization, regional settings, lifecycle transitions, restaurant memberships).
- **Branch management** (physical locations with independent timezones, addresses, geo-coordinates, lifecycle transitions, and branch-level staff assignments).
- **Memberships & invitations** (SHA-256 hashed invitation tokens, expiry/email verification, atomic final-owner protection).
- **Frontend workflows** across `apps/web` and `apps/admin` backed by `@menu-it/shared-types`.

---

## 2. Key Architectural & Implementation Highlights
- **Pure Domain Layer (`menu_it.domain.*`)**: Added `OrganizationEntity`, `OrganizationSettingsEntity`, `RestaurantEntity`, `RestaurantSettingsEntity`, `BranchEntity`, `BranchLifecycleState`, `OrganizationMembershipEntity`, `RestaurantMembershipEntity`, `BranchAssignmentEntity`, and `OrganizationInvitationEntity` with zero infrastructure imports.
- **Database & RLS (`0009_fcd14_org_branch`)**: Added `branches`, `branch_assignments`, `organization_invitations`, `organization_settings`, and `restaurant_settings` with composite foreign keys (`fk_branches_org_restaurant`, `fk_branch_assignments_org_branch`) and `ENABLE`/`FORCE ROW LEVEL SECURITY` policies.
- **Application Services & Transactional Outbox**: Implemented `OrganizationManagementService`, `RestaurantManagementService`, `BranchManagementService`, and `MembershipAndInvitationService`, publishing domain events via `OutboxEventPublisher` and recording `OrganizationAuditEvent` trails atomically.
- **API & Frontend**: Registered `/api/v1/organizations`, `/api/v1/restaurants`, and `/api/v1/branches` endpoints (57 total OpenAPI paths), updated `@menu-it/shared-types`, built `apps/web/src/services/org-api.ts`, and implemented onboarding, organization, restaurant, branch, and member management pages in `apps/web` and `apps/admin`.
