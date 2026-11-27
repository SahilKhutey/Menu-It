# FCD-12 · Document 14: Deployment Validation, Smoke Tests & Rollback

**Phase:** FCD-12 — Automated Testing & CI/CD Foundation  
**System:** Menu-It Restaurant SaaS Platform  
**Status:** Completed & Approved  
**Date:** 2026-11-26  

---

## 1. Post-Deployment Smoke Verification

Following any deployment to staging or production, the automated smoke verification script `tests/deployment/smoke.py` is invoked:
- Verifies API liveness: `GET /api/v1/health` (HTTP 200)
- Verifies database readiness: `GET /api/v1/health/database` (HTTP 200)
- Verifies system info: `GET /api/v1/system/info` (HTTP 200)
- Verifies telemetry metrics: `GET /api/v1/metrics` (HTTP 200)

If any check returns non-200 or times out, the deployment is marked as failed.

---

## 2. Rollback Execution Matrix

| Failure Mode | Immediate Rollback Action | Data Impact |
| :--- | :--- | :--- |
| **Pod CrashLoopBackOff** | Fast rollback to previous container image digest via Kubernetes deployment undo | Zero data loss |
| **Database Migration Error** | Halt deployment; execute migration downgrade if expand-and-contract | Relational state preserved |
| **Smoke Test Failure** | Revert traffic routing to existing healthy pod pool; investigate logs | Zero downtime |
| **Critical Regression** | Roll back frontend & backend image digests to prior version | Seamless reversion |
