# FCD-11 · Document 02: Threat Modeling & Risk Assessment

**Phase:** FCD-11 — Security, Reliability & Observability Foundation  
**System:** Menu-It Restaurant SaaS Platform  
**Status:** Completed & Approved  
**Date:** 2026-11-26  

---

## 1. Threat Modeling Methodology

The Menu-It platform applies the **STRIDE** threat categorization model across all primary components, actors, data stores, and external integrations.

### STRIDE Assessment Matrix

| Threat Category | Potential Attack Vector in Menu-It | Mitigation & Architectural Control |
| :--- | :--- | :--- |
| **Spoofing** | Forged JWT token or fake tenant identity claim | Asymmetric signature verification; issuer/audience claims validation; database-backed session state; no client-controlled tenant IDs accepted without authorization |
| **Tampering** | Parameter tampering on tenant IDs or order amounts | Pydantic strict schemas; immutable Domain Models; DB Row Level Security; append-only audit logs |
| **Repudiation** | Actor denies initiating password reset, order cancel, or config modification | Durable `security_audit_events` logging actor ID, IP address, user agent, timestamp, action, and outcome |
| **Information Disclosure** | Cross-tenant data bleed or credential leakage in stack traces | Dual-layer tenant isolation (app + DB RLS); centralized exception handlers masking internal errors; recursive redaction on logs |
| **Denial of Service** | Volumetric brute-force login attacks or runaway API traffic | Distributed `RedisRateLimiter` sliding-window quotas; connection pooling; bounded request timeouts; circuit breakers |
| **Elevation of Privilege** | Tenant user tampering with permissions to access platform admin endpoints | Deny-by-default permission checks (`require_permission`); role hierarchy; explicit platform membership table separation |

---

## 2. Risk Register & Prioritization

1. **RR-01 Cross-Tenant Data Access (Critical):** Mitigated by automated RLS policies on PostgreSQL and application-level `assert_tenant_boundary`.
2. **RR-02 Credential Stuffing & Brute Force (High):** Mitigated by rate limiting (5 failed login lockouts), Argon2id computational resistance, and security audit telemetry.
3. **RR-03 Insecure Production Deployment (High):** Mitigated by `ensure_production_config` blocking application startup if weak secrets, debug mode, or unencrypted cookies are present.
4. **RR-04 Dependency Supply Chain Vulnerability (Medium):** Mitigated by automated package auditing (`pip-audit`, `pnpm audit`) and pinned dependencies.
