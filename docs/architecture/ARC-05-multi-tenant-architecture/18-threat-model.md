# 18 — Multi-Tenant Threat Model & STRIDE Analysis

## 1. Threat Mitigation Matrix (ARC05-TH01 – ARC05-TH18)

| Threat ID | Category | Threat Vector | Primary Mitigation |
|---|---|---|---|
| ARC05-TH01 | Elevation | IDOR parameter tampering | Server-side ownership validation |
| ARC05-TH02 | Spoofing | Client-supplied tenant ID forged | Server-derived TenantContext |
| ARC05-TH03 | Disclosure | Missing WHERE organization_id | Scoped repositories + PostgreSQL RLS |
| ARC05-TH04 | Tampering | Cross-tenant write / update | RLS WITH CHECK policy |
| ARC05-TH05 | Elevation | Client sends role='owner' | Server-owned role assignment |
| ARC05-TH06 | Elevation | Branch access bypass | Branch-level authorization policy |
| ARC05-TH07 | Disclosure | Cache namespace collision | Tenant-prefixed cache keys |
| ARC05-TH08 | Disclosure | Media bucket traversal | Backend-generated keys & HMAC signed URLs |
| ARC05-TH09 | Tampering | Worker context leakage | TenantJobContext & cleanup |
| ARC05-TH10 | Elevation | Runtime DB role bypasses RLS | Least-privilege role (NOBYPASSRLS) |
| ARC05-TH11 | Disclosure | Unpublished draft leaked to diner | Published-only read model |
| ARC05-TH12 | Elevation | Support operator abuse | Time-bound, ticket-scoped access |
| ARC05-TH13 | Tampering | Backup restore contamination | Tenant-scoped recovery tooling |
| ARC05-TH14 | Spoofing | Invitation token interception | Cryptographic single-use tokens |
| ARC05-TH15 | Tampering | Cross-tenant child relationship | Composite foreign key constraints |
| ARC05-TH16 | Disclosure | Connection pool context leakage | Transaction-local settings (is_local=true) |
| ARC05-TH17 | Recon | Organization ID enumeration | Masked 404 responses & rate limits |
| ARC05-TH18 | Tampering | Cross-tenant entitlement theft | Tenant-scoped subscription check |
