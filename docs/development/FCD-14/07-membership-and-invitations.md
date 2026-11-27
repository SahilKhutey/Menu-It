# FCD-14 — 07 Membership & Invitations

## Service Implementation
`MembershipAndInvitationService` (`apps/api/src/menu_it/services/membership_and_invitation.py`) manages organization members and onboarding invitations.

## Invitation Workflow
1. **`create_invitation`**: Generates a high-entropy raw token (`secrets.token_urlsafe(32)`), stores only its SHA-256 `token_hash` in `organization_invitations` with `expires_at`, emits `InvitationCreated` outbox event, and triggers notification dispatch.
2. **`list_invitations` / `revoke_invitation`**: Lists pending/historical invitations or revokes a pending invitation.
3. **`accept_invitation`**: Hashes the presented `raw_token`, locates the invitation, normalizes naive SQLite timestamps if needed, validates via `ensure_invitation_acceptable` (checking status, expiry, and case-insensitive actor email match), creates/activates `OrganizationMembership`, marks the invitation `ACCEPTED`, and emits `InvitationAccepted`.
