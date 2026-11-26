# FCD-11 · Document 04: Secrets Management & Credential Lifecycle

**Phase:** FCD-11 — Security, Reliability & Observability Foundation  
**System:** Menu-It Restaurant SaaS Platform  
**Status:** Completed & Approved  
**Date:** 2026-11-26  

---

## 1. Secrets Governance & Storage

1. **No Hardcoded Secrets:** No secrets, credentials, or production private keys may be committed to version control.
2. **Environment Variable Injection:** Runtime secrets are supplied via environment variables (`.env` in local development; Kubernetes secrets or HashiCorp Vault in production).
3. **Automated Startup Validation:**
   - In production (`app_env == "production"`), `ensure_production_config` inspects `AUTH_SECRET_KEY`, `DATABASE_URL`, and cookie security flags.
   - If placeholder strings (`dev-insecure`, `changeme`, `replace_me`) or keys shorter than 32 characters are detected, the application terminates immediately with a `SecurityConfigurationError`.

---

## 2. Credential Rotation Procedures

### JWT Signing Key Rotation
1. **Asymmetric (RS256):**
   - New keypair is generated: `menu-it-k2`.
   - Public key `menu-it-k2` is published to the JWKS endpoint alongside existing `menu-it-k1`.
   - The API is updated to sign new tokens with `menu-it-k2`.
   - Verification accepts tokens signed with either `menu-it-k1` or `menu-it-k2`.
   - After the maximum refresh token lifetime (30 days), `menu-it-k1` is decommissioned.

### Database Password Rotation
1. Update database user password in PostgreSQL using connection pool zero-downtime rotation.
2. Update Kubernetes secret / Vault entry with the new connection string.
3. Rolling restart of FastAPI backend pods to establish connections with new credentials.
4. Verify `/api/v1/health/database` reports healthy status.
