# FCD-13 · Document 10 — Environment & Configuration Readiness

## 1. Objective
Establishes typed, validated, and environment-specific configuration across all platform tiers (`development`, `test`, `staging`, `production`) to prevent secret leakage and configuration drift.

---

## 2. Environment Matrix

| Environment Tier | Purpose | Dataset | Credential Scoping |
| :--- | :--- | :--- | :--- |
| **Local** | Developer day-to-day work | Synthetic local seed | Local-only docker-compose credentials |
| **CI** | Ephemeral automated testing | Dynamic fixtures | Short-lived test credentials in GitHub Actions |
| **Testing** | Automated integration | Synthetic test fixtures | Isolated testing environment secrets |
| **Staging** | Production release rehearsal | Masked / synthetic dataset | Staging secrets (replicates production topology) |
| **Production**| Live customer workloads | Authoritative tenant data | Production KMS/secrets manager |

---

## 3. Configuration Security Rules

1. **Strict Pydantic Validation:**
   - Configuration is validated at boot via `menu_it.core.config.Settings`.
   - Unknown environment names or out-of-range port numbers raise a `ValidationError`, halting startup safely.
2. **Zero Hardcoded Production Secrets:**
   - Database passwords, JWT secret keys, and encryption credentials must be provided via environment variables.
3. **Frontend Secret Boundary:**
   - Frontend apps (`apps/web`, `apps/admin`) only expose variables prefixed with `NEXT_PUBLIC_`.
   - Backend database and JWT keys are excluded from Next.js client bundles.
4. **CORS Restrictions in Production:**
   - Wildcard CORS (`*`) is strictly rejected in staging and production environments.

---

## 4. Verification Evidence
Verified by: `apps/api/tests/integration/test_lifecycle_integration.py` (`test_invalid_configuration_fails_safely`).
