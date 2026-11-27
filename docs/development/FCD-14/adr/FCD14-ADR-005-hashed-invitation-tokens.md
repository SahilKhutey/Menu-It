# FCD14-ADR-005: SHA-256 Hashed Organization Invitation Tokens

## Status
Accepted

## Context
Persisting plaintext invitation tokens creates bearer-token exposure if database backups or read replicas are compromised.

## Decision
Generate high-entropy raw tokens (`secrets.token_urlsafe(32)`) in `MembershipAndInvitationService.create_invitation`, deliver the raw token once to the notification channel/caller, and store only its SHA-256 hex digest (`token_hash`) in `organization_invitations`.

## Consequences
- Database reads cannot replay pending invitations; verification compares `sha256(raw_token)` against `token_hash`.
