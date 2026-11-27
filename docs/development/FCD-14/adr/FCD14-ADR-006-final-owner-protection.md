# FCD14-ADR-006: Atomic Final Owner Protection

## Status
Accepted

## Context
Demoting or removing the sole active `OWNER` of an organization would lock the tenant out of administrative and billing controls.

## Decision
Enforce `ensure_not_removing_final_owner` in `domain/membership/policies.py` and invoke it inside `MembershipAndInvitationService.update_member` and `remove_member` before committing any owner demotion or removal.

## Consequences
- Guarantees every active organization always has at least one active owner.
