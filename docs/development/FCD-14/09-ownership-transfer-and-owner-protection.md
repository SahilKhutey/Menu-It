# FCD-14 — 09 Ownership Transfer & Owner Protection

## Final Owner Protection
Organizations must always retain at least one `ACTIVE` member with `OrganizationRole.OWNER`.
- `MembershipAndInvitationService.update_member` (when demoting an `OWNER`) and `remove_member` (when revoking/deleting an `OWNER`) count active owners and invoke `ensure_not_removing_final_owner`.
- Attempting to demote or remove the last active owner raises `BusinessRuleViolationError` (mapped to HTTP 422/409).

## Atomic Ownership Transfer
`MembershipAndInvitationService.transfer_ownership`:
1. Verifies the actor is an active `OWNER` and the target user holds an active `OrganizationMembership` in the same organization.
2. Promotes the target member to `OrganizationRole.OWNER`.
3. Optionally demotes the previous owner to `OrganizationRole.ADMIN` within the same transaction.
4. Emits `OrganizationOwnershipTransferred` outbox event and `OrganizationAuditEvent`.
