# FCD-12 · Document 18: Production Release Checklist

**Phase:** FCD-12 — Automated Testing & CI/CD Foundation  
**System:** Menu-It Restaurant SaaS Platform  
**Status:** Completed & Approved  
**Date:** 2026-11-26  

---

## 1. Pre-Deployment Release Gates

Before initiating a production deployment:

1. [x] **CI Verification:** All checks in `.github/workflows/ci.yml` pass on `main`.
2. [x] **Image Digests:** Container digests for `menu-it-api`, `menu-it-web`, and `menu-it-admin` recorded.
3. [x] **Database Backup:** PostgreSQL point-in-time recovery backup confirmed healthy (< 15 min old).
4. [x] **Migration Compatibility:** Non-destructive expand-and-contract migrations verified against staging.
5. [x] **Production Approval:** Explicit sign-off recorded in GitHub Actions Environment review.

---

## 2. Post-Deployment Verification

1. [x] Rolling deployment completes across all pods without pod restart loops.
2. [x] Smoke tests (`tests/deployment/smoke.py`) report 100% healthy status.
3. [x] Prometheus metrics (`GET /api/v1/metrics`) stream telemetry without elevation in 5xx errors.
4. [x] Release evidence packaged and archived via `.github/workflows/release.yml`.
