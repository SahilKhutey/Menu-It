# FCD-14 — 12 Audit Logging & Notifications

## Security & Organization Audit Events
Every administrative mutation across organizations, restaurants, branches, memberships, and invitations records an `OrganizationAuditEvent` (FCD-09) capturing `organization_id`, `actor_user_id`, `action`, `resource_type`, `resource_id`, and structured metadata.

## Invitation Notifications
When `MembershipAndInvitationService.create_invitation` issues an invitation, it queues/dispatches an invitation notification using the FCD-09 notification channel infrastructure, delivering the raw invitation token (which is never stored in plaintext in the database) to the invitee's email address.
