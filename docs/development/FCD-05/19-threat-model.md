# FCD-05 — Threat Model & Mitigation Analysis

## 1. STRIDE Threat Analysis Matrix

| STRIDE Category | Threat Description | Architectural Mitigation | Status |
|---|---|---|:---:|
| **Spoofing** | Attacker crafts a forged JWT claiming administrative identity. | All JWTs verified against secret key; issuer & audience enforced; `none` algorithm rejected. | Mitigated |
| **Spoofing** | Attacker impersonates an existing user during signup. | Email verification required; unverified accounts cannot perform sensitive actions. | Mitigated |
| **Tampering** | Attacker modifies tenant claims or user IDs in HTTP headers. | Tenant and platform context resolved exclusively server-side from database memberships. | Mitigated |
| **Tampering** | Man-in-the-middle modifies refresh token in transit. | Delivered in `HttpOnly`, `Secure`, `SameSite=Lax` cookies; HTTPS required. | Mitigated |
| **Repudiation** | Malicious actor denies performing sensitive administrative action. | Non-repudiable audit events emitted on every security state change; database tracks `user_id`. | Mitigated |
| **Information Disclosure** | Timing attack reveals whether an email is registered during login. | Constant-time dummy verification executed when user is not found. | Mitigated |
| **Information Disclosure** | Attacker enumerates tenant organizations by probing IDs. | Absent tenant membership raises HTTP 404 (Not Found) rather than 403 (Forbidden). | Mitigated |
| **Denial of Service** | Credential stuffing / password brute-force floods login endpoint. | Network-level rate limiting + per-account lockout after 5 consecutive failures. | Mitigated |
| **Elevation of Privilege**| Organization Owner attempts to access SaaS platform admin endpoints. | Strict privilege separation; platform roles stored in separate table gated by `require_platform_role`. | Mitigated |
