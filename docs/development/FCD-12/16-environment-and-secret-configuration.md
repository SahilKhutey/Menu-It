# FCD-12 · Document 16: Environment & Secret Configuration

**Phase:** FCD-12 — Automated Testing & CI/CD Foundation  
**System:** Menu-It Restaurant SaaS Platform  
**Status:** Completed & Approved  
**Date:** 2026-11-26  

---

## 1. Environment Segregation

GitHub Environments configure isolation and access boundaries:
- **`testing`:** Fully automated deployment environment.
- **`staging`:** Production-like pre-release environment for end-to-end verification.
- **`production`:** Restricted environment requiring mandatory human approval from designated maintainers before release execution.

---

## 2. Secrets Management Matrix

| Secret Name | Scope | Description |
| :--- | :--- | :--- |
| `DATABASE_URL` | Staging / Production | Production PostgreSQL connection string |
| `REDIS_URL` | Staging / Production | Redis caching cluster connection string |
| `AUTH_SECRET_KEY` | Staging / Production | Minimum 256-bit cryptographically random JWT signing key |
| `CONTAINER_REGISTRY_TOKEN`| Repository Secrets | Token for pushing to container registry |
