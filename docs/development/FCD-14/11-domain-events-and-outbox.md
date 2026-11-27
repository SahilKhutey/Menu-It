# FCD-14 — 11 Domain Events & Transactional Outbox

## Outbox Integration
All FCD-14 state mutations publish domain events through `OutboxEventPublisher` (FCD-10) within the same database transaction as the entity mutation.

## Events Published
- **Organization**: `OrganizationCreated`, `OrganizationUpdated`, `OrganizationSuspended`, `OrganizationOwnershipTransferred`
- **Restaurant**: `RestaurantCreated`, `RestaurantUpdated`, `RestaurantStatusChanged`
- **Branch**: `BranchCreated`, `BranchUpdated`, `BranchStatusChanged`, `BranchStaffAssigned`, `BranchStaffRemoved`
- **Membership & Invitations**: `OrganizationMemberUpdated`, `OrganizationMemberRemoved`, `InvitationCreated`, `InvitationRevoked`, `InvitationAccepted`

## Atomicity Guarantee
Because events are written to `event_outbox` in the same `AsyncSession` transaction, no event is lost on commit or published on rollback.
