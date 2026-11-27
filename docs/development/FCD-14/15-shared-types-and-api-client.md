# FCD-14 — 15 Shared Types & API Client

## Shared TypeScript Contracts (`packages/shared-types`)
- `packages/shared-types/src/organization.ts`: `OrganizationDTO`, `OrganizationSettingsDTO`, `OrganizationMemberDTO`, `OrganizationInvitationDTO`, `OrganizationRole`, `MembershipStatus`, and create/update payload interfaces.
- `packages/shared-types/src/branch.ts`: `BranchDTO`, `BranchAssignmentDTO`, `BranchStatus`, `BranchRole`, and create/update/assignment payload interfaces.
- `packages/shared-types/src/index.ts`: Re-exports all FCD-14 types cleanly across workspace packages.

## Web API Client (`apps/web/src/services/org-api.ts`)
Typed wrapper over `apiRequest<T>` (`apps/web/src/services/api-client.ts`) providing methods for organization onboarding, settings, restaurants, branches, memberships, invitations, and branch assignments.
