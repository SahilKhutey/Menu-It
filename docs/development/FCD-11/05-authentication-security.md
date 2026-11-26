# FCD-11 · Document 05: Identity, Authentication & Session Security

**Phase:** FCD-11 — Security, Reliability & Observability Foundation  
**System:** Menu-It Restaurant SaaS Platform  
**Status:** Completed & Approved  
**Date:** 2026-11-26  

---

## 1. Authentication Architecture

Menu-It enforces strong identity verification:
1. **Password Security:** Salted and hashed using Argon2id with strict parameters (time_cost=3, memory_cost=65536 KiB, parallelism=4).
2. **Session Lifecycles:**
   - Short-lived Access Tokens (10 minutes / 600s).
   - Long-lived Refresh Tokens (30 days / 2,592,000s) stored in hashed form in the database (`refresh_tokens` table) with rotation on every refresh.
   - Immediate session revocation capability across all devices or per-session.
3. **Brute Force Lockout:** 5 consecutive failed login attempts trigger an automatic 15-minute account lockout, generating a `auth.login.lockout` security audit event.
4. **Cookie Security:** In production, cookies are tagged `Secure; HttpOnly; SameSite=Lax`.

---

## 2. Session Revocation Flow

When a user triggers logout or password change:
1. Active session marked `revoked` in `user_sessions`.
2. Associated refresh token hash is deleted.
3. Security audit event `session.revoked` or `auth.password.changed` is emitted.
4. Any subsequent attempt to use the revoked access or refresh token results in HTTP 401 Unauthorized.
