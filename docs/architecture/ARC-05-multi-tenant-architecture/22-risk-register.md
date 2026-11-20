# 22 — Tenancy Risk Register

## Risk Register (ARC05-R01 – ARC05-R20)

| Risk ID | Risk Description | Severity | Mitigation | Status |
|---|---|---|---|---|
| ARC05-R01 | Incorrect tenant resolution | Critical | Server-derived context | Mitigated |
| ARC05-R02 | Missing tenant filter in queries | Critical | Scoped repositories + RLS | Mitigated |
| ARC05-R03 | Incorrect resource ownership | Critical | Ownership manifest | Mitigated |
| ARC05-R04 | RLS misconfiguration | Critical | Policy coverage tests | Mitigated |
| ARC05-R05 | Privileged DB runtime role | Critical | Restricted credentials | Mitigated |
| ARC05-R06 | Pooled connection context leak | Critical | Transaction-local config | Mitigated |
| ARC05-R07 | Cache cross-tenant leakage | Critical | Prefixed namespaces | Mitigated |
| ARC05-R08 | Private media exposure | High | Authorized signed URLs | Mitigated |
| ARC05-R09 | Role escalation | Critical | Server-side policy | Mitigated |
| ARC05-R10 | Branch access bypass | High | Branch assignment check | Mitigated |
| ARC05-R11 | Public draft exposure | Critical | Published-only read path | Mitigated |
| ARC05-R12 | Background worker leak | Critical | TenantJobContext | Mitigated |
| ARC05-R13 | Support access abuse | High | Time-bound ticket auth | Mitigated |
| ARC05-R14 | Tenant deletion spillover | Critical | Scoped deletion + tests | Mitigated |
| ARC05-R15 | Cross-tenant relationship | Critical | Composite foreign keys | Mitigated |
| ARC05-R16 | Stale revoked permissions | High | Revocation cache eviction | Mitigated |
| ARC05-R17 | Tenant ID enumeration | Medium | Masked 404 responses | Mitigated |
| ARC05-R18 | Self-hosted logic drift | High | Shared domain interfaces | Mitigated |
| ARC05-R19 | Suspension diner shock | Medium | Documented grace period | Mitigated |
| ARC05-R20 | Secrets in audit logs | High | Automated log redaction | Mitigated |
