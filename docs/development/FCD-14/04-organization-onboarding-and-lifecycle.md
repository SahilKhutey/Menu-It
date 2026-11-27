# FCD-14 — 04 Organization Onboarding & Lifecycle

## Service Implementation
`OrganizationManagementService` (`apps/api/src/menu_it/services/organization_management.py`) orchestrates organization lifecycle and settings within a single database transaction.

## Onboarding Flow (`create_organization`)
1. Validates input slug uniqueness (`ResourceConflictError` on duplicate slug).
2. Creates the `Organization` record (initially `ACTIVE`) and default `OrganizationSettings`.
3. Creates the founding `OrganizationMembership` with `OrganizationRole.OWNER` and `MembershipStatus.ACTIVE`.
4. Emits an `OrganizationCreated` outbox event via `OutboxEventPublisher` and writes an `OrganizationAuditEvent`.

## Updates & Suspension
- `update_organization`: Updates profile/contact fields and emits audit + outbox events.
- `get_settings` / `update_settings`: Reads and updates `OrganizationSettings`.
- `suspend_organization`: Uses FCD-04 `transition_organization` lifecycle state machine to move an organization to `SUSPENDED` and records audit/outbox entries.
