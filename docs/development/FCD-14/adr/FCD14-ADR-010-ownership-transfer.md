# FCD14-ADR-010: Atomic Organization Ownership Transfer

## Status
Accepted

## Context
Handing over an organization requires promoting a new owner while optionally demoting the departing owner without ever triggering a zero-owner state.

## Decision
Implement `MembershipAndInvitationService.transfer_ownership` as a single atomic transaction that validates both actor (`OWNER`) and target (`ACTIVE` member), promotes the target to `OWNER`, optionally demotes the previous owner to `ADMIN`, and records audit + outbox events.

## Consequences
- Eliminates race conditions or invalid intermediate states during ownership handoff.
