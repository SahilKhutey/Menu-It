# FCD-12 · Document 12: Branch Protection & Pull Request Governance

**Phase:** FCD-12 — Automated Testing & CI/CD Foundation  
**System:** Menu-It Restaurant SaaS Platform  
**Status:** Completed & Approved  
**Date:** 2026-11-26  

---

## 1. Branch Protection Rules

### `main` Branch (Production)
- Require pull request before merging.
- Require all mandatory CI status checks to pass (`ci-summary`).
- Restrict direct pushes (strictly forbidden).
- Enforce linear git history; require branches to be up to date before merging.

### `develop` Branch (Integration)
- Require pull request before merging.
- Require `ci-summary` workflow pass.
- Block force pushes and branch deletion.

---

## 2. Required Status Checks

The mandatory status check registered in GitHub branch protection is **`CI Quality Gate Summary`** (`ci-summary` in `.github/workflows/ci.yml`), which validates that all child gates succeed:
- `repository-validation`
- `backend-quality`
- `frontend-quality`
- `database-integration`
- `security-scan`
