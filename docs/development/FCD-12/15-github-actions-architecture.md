# FCD-12 · Document 15: GitHub Actions CI/CD Architecture

**Phase:** FCD-12 — Automated Testing & CI/CD Foundation  
**System:** Menu-It Restaurant SaaS Platform  
**Status:** Completed & Approved  
**Date:** 2026-11-26  

---

## 1. Workflow Catalog

| Workflow File | Trigger | Purpose |
| :--- | :--- | :--- |
| **`ci.yml`** | PR / Push to `main`, `develop` | Primary unified quality gate orchestrator |
| **`backend-tests.yml`** | Backend paths changed | Ruff format, Ruff lint, Pytest, coverage XML |
| **`frontend-tests.yml`** | Frontend paths changed | Prettier, ESLint, TypeScript, Vitest, Next.js builds |
| **`database-tests.yml`** | DB/Alembic paths changed | Ephemeral PostgreSQL, single head check, migrations |
| **`security.yml`** | Code changes / Weekly cron | Bandit, pip-audit, pnpm audit, secret scans |
| **`e2e.yml`** | Web/Admin changes | Playwright browser workflow tests |
| **`build-images.yml`** | Push to `develop`, `main`, tags | Docker Buildx builds for API, Web, and Admin |
| **`deploy-staging.yml`** | Push to `develop` | Staging rollout, migrations, and smoke tests |
| **`deploy-production.yml`**| Manual workflow dispatch | Approval-gated production release & smoke tests |
| **`release.yml`** | Push tag (`v*`, `fcd-*`) | Evidence packaging and GitHub Release creation |
