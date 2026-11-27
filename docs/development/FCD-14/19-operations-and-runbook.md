# FCD-14 — 19 Operations & Runbook

## Operational Checks
- **Schema Verification**: Run `alembic current` and `alembic heads` before release to confirm `0009_fcd14_org_branch` is applied.
- **Outbox Monitoring**: Monitor `event_outbox` for `Organization*`, `Restaurant*`, `Branch*`, and `Invitation*` event delivery latency and dead-letter counts.
- **Invitation Expiry & Cleanup**: Expired pending invitations are rejected at acceptance time by `ensure_invitation_acceptable`; periodic cleanup jobs can prune stale expired rows without impacting active memberships.
- **Emergency Organization Suspension**: Platform administrators can suspend an organization via `POST /api/v1/organizations/{organization_id}/suspend`, which records an audit trail and emits `OrganizationSuspended`.
