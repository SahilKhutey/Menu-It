# FCD-11 · Document 23: Security Incident Detection, Triage & Response Protocols (IR-01 to IR-08)

**Phase:** FCD-11 — Security, Reliability & Observability Foundation  
**System:** Menu-It Restaurant SaaS Platform  
**Status:** Completed & Approved  
**Date:** 2026-11-26  

---

## 1. Incident Response Lifecycle

Menu-It follows the NIST SP 800-61 Incident Handling Guide:
1. **Preparation:** Instrumentation, log forwarding, runbooks, and role assignments.
2. **Detection & Analysis:** Automated alerts, anomaly thresholds, and audit log monitoring.
3. **Containment:** Rate limiting, session revocation, credential rotation, network isolation.
4. **Eradication:** Patching vulnerabilities, removing unauthorized access.
5. **Recovery:** Restoring services, validating data consistency, monitoring traffic.
6. **Post-Incident Activity:** Post-mortem review, timeline documentation, and preventative action items.

---

## 2. Standardized Incident Runbooks (IR-01 through IR-08)

### IR-01: Credential Stuffing & High-Volume Brute Force
- **Trigger:** Elevated rate limit breaches on `/api/v1/auth/login` or `auth.login.failed` alerts.
- **Action:** Verify automated lockout active; block attacking IP ranges at edge WAF; force CAPTCHA or delay if necessary.

### IR-02: Tenant Boundary Breach Attempt
- **Trigger:** `tenant.boundary_breach_attempt` security audit event logged.
- **Action:** Immediate on-call alert; inspect actor user ID and session; terminate active session; review audit trail for any successful prior queries.

### IR-03: Stolen Session or Leaked Token
- **Trigger:** Impossible travel detection or user reports unexpected activity.
- **Action:** Revoke all sessions for user via `/api/v1/sessions/revoke-all`; rotate password; invalidate active refresh tokens.

### IR-04: Production Secrets Leakage
- **Trigger:** Secret scanning detection in repository or external paste site.
- **Action:** Immediately rotate the affected key; redeploy application; audit access logs during the exposure window for unauthorized usage.

### IR-05: Distributed Denial of Service (DDoS)
- **Trigger:** API latency spike, 502/504 edge gateway errors, traffic volume exceeding 5x baseline.
- **Action:** Enable Cloudflare / edge proxy "Under Attack" mode; enforce aggressive rate limits; scale backend pods.

### IR-06: Database Corruption or Accidental Data Loss
- **Trigger:** Integrity error alerts or customer reports missing records.
- **Action:** Freeze writes; initiate Point-in-Time Recovery (PITR) to a separate database instance; verify table state; execute surgical backfill.

### IR-07: Third-Party Service Dependency Outage
- **Trigger:** `CircuitBreakerOpenException` alerts on payment, notification, or storage providers.
- **Action:** Verify status page of vendor; notify customer support; ensure graceful degradation messages surface on frontend.

### IR-08: Supply Chain or Zero-Day Vulnerability
- **Trigger:** CVE disclosure affecting core framework (FastAPI, SQLAlchemy, Next.js).
- **Action:** Assess vulnerability impact; apply vendor patch or temporary WAF mitigations; verify tests and deploy hotfix.
