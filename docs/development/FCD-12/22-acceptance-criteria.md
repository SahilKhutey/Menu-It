# FCD-12 · Document 22: FCD-12 Acceptance Criteria

**Phase:** FCD-12 — Automated Testing & CI/CD Foundation  
**System:** Menu-It Restaurant SaaS Platform  
**Status:** Completed & Approved  
**Date:** 2026-11-26  

---

## 1. Scope of Criteria

This document defines the 36 specific acceptance criteria (`AC-01` through `AC-36`) that govern the completion and sign-off of Phase FCD-12.

### Criteria Categories
1. **Repository & Backend Quality (AC-01 to AC-08):** Baseline audit, testing strategy, Pytest configuration, Ruff formatting/linting, type checking, unit tests, API tests, and coverage reporting.
2. **Frontend Quality (AC-09 to AC-13):** Vitest framework configuration, web and admin unit tests, and production builds.
3. **Database & API Integration (AC-14 to AC-18):** PostgreSQL ephemeral service, Alembic migration tests, restricted role RLS enforcement, connection pool reuse, and API contract validation.
4. **E2E & Security Testing (AC-19 to AC-26):** Playwright setup, customer and admin workflows, secret scanning, dependency vulnerability audits, SAST, and container scans.
5. **CI/CD Orchestration (AC-27 to AC-32):** Performance baselines, GitHub Actions pinning, PR quality gate enforcement, branch protection, reproducible Docker builds, and commit-traceable digests.
6. **Deployment & Release Controls (AC-33 to AC-36):** Staging/testing environments, production approvals, post-deployment smoke verification, and release evidence documentation.
