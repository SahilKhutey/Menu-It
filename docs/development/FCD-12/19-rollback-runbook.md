# FCD-12 · Document 19: Emergency Rollback Runbook

**Phase:** FCD-12 — Automated Testing & CI/CD Foundation  
**System:** Menu-It Restaurant SaaS Platform  
**Status:** Completed & Approved  
**Date:** 2026-11-26  

---

## 1. Rollback Decision Triggers

Initiate immediate rollback if any of the following conditions occur within 30 minutes of deployment:
1. Error rate (`5xx responses / total requests`) exceeds 1.0% for > 3 consecutive minutes.
2. API p95 response latency degrades beyond 1,500ms.
3. Smoke verification (`tests/deployment/smoke.py`) fails with health probe timeouts.
4. Database deadlock or connection pool exhaustion is detected.

---

## 2. Step-by-Step Rollback Procedure

1. **Step 1: Application Traffic Reversion**
   - In Kubernetes, run: `kubectl rollout undo deployment/menu-it-api`
   - Revert web and admin frontends to prior verified image digests.
2. **Step 2: Database Assessment**
   - If backward-compatible expand-and-contract migrations were used, the prior application version can continue running on the current schema without downgrade.
   - If downgrade is required, execute `alembic downgrade <previous_revision>`.
3. **Step 3: Verification & Triage**
   - Re-run `python tests/deployment/smoke.py` to confirm restoration of normal service.
   - Post incident status to customer communication channels and initiate post-mortem analysis.
