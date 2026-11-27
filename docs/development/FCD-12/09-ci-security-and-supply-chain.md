# FCD-12 · Document 09: CI Security & Software Supply Chain

**Phase:** FCD-12 — Automated Testing & CI/CD Foundation  
**System:** Menu-It Restaurant SaaS Platform  
**Status:** Completed & Approved  
**Date:** 2026-11-26  

---

## 1. Supply Chain Hardening

1. **Exact Dependency Locking:**
   - Python dependencies locked via `pyproject.toml`.
   - Node dependencies locked via `pnpm-lock.yaml`.
   - CI uses frozen lockfile installation (`pnpm install --frozen-lockfile`).
2. **Least-Privilege GitHub Actions Permissions:**
   - Default workflow permissions set to `permissions: contents: read`.
   - Publishing workflows explicitly request `packages: write` or `contents: write` only where necessary.
3. **Action Pinning:**
   - GitHub Actions are pinned to verified versions (e.g. `actions/checkout@v4`, `actions/setup-python@v5`).

---

## 2. Untrusted Pull Request Isolation

- PRs originating from forks do not have access to GitHub environment secrets or production credentials.
- Container image pushes and deployments only occur on authenticated pushes to protected branches (`main`, `develop`) or version tags.
