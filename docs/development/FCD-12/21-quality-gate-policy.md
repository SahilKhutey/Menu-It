# FCD-12 · Document 21: Architecture Decision Records (FCD12-ADR-001 to FCD12-ADR-012)

**Phase:** FCD-12 — Automated Testing & CI/CD Foundation  
**System:** Menu-It Restaurant SaaS Platform  
**Status:** Completed & Approved  
**Date:** 2026-11-26  

---

## FCD12-ADR-001: CI/CD Platform & Workflow Structure
- **Decision:** Use GitHub Actions with reusable workflow files (`backend-tests.yml`, `frontend-tests.yml`, `database-tests.yml`, `security.yml`) coordinated by a single required orchestrator (`ci.yml`).
- **Status:** Approved & Implemented.

## FCD12-ADR-002: Monorepo Package Management & Lockfile Policy
- **Decision:** Use `pnpm` with `--frozen-lockfile` for frontend and `pip` with locked dependencies for backend to ensure 100% reproducible builds.
- **Status:** Approved & Implemented.

## FCD12-ADR-003: Testing Pyramid & Quality Thresholds
- **Decision:** Multi-tier testing pyramid: fast unit tests on every PR, ephemeral PostgreSQL database tests, and Playwright browser tests.
- **Status:** Approved & Implemented.

## FCD12-ADR-004: Ephemeral PostgreSQL for Migration & RLS Testing
- **Decision:** Run database tests against genuine PostgreSQL 16 service containers rather than relying exclusively on SQLite, ensuring composite FKs and RLS are fully exercised.
- **Status:** Approved & Implemented.

## FCD12-ADR-005: Playwright for Cross-Application E2E Testing
- **Decision:** Adopt Playwright for browser-level testing of customer menu browsing, admin login, and tenant isolation flows.
- **Status:** Approved & Implemented.

## FCD12-ADR-006: Multi-Scanner Security Gate Policy
- **Decision:** Enforce Gitleaks secret scanning, Bandit Python SAST, pip-audit, and pnpm audit; fail-closed on verified critical/high vulnerabilities.
- **Status:** Approved & Implemented.

## FCD12-ADR-007: Container Build & Immutable Digest Tagging
- **Decision:** Build multi-stage Docker images (`menu-it-api`, `menu-it-web`, `menu-it-admin`) running as non-root users and tag with Git commit SHAs and SHA-256 digests.
- **Status:** Approved & Implemented.

## FCD12-ADR-008: Controlled Multi-Environment Deployment Pipeline
- **Decision:** Structure deployment progression across Testing, Staging, and Production environments using GitHub Environments.
- **Status:** Approved & Implemented.

## FCD12-ADR-009: Expand-and-Contract Database Migrations
- **Decision:** Apply backward-compatible migrations prior to application pod updates, allowing zero-downtime rolling updates.
- **Status:** Approved & Implemented.

## FCD12-ADR-010: Semantic Versioning & Release Evidence Packages
- **Decision:** Use SemVer 2.0.0 (`MAJOR.MINOR.PATCH`) and generate immutable `release-metadata.json` packages for every published tag.
- **Status:** Approved & Implemented.

## FCD12-ADR-011: Automated Smoke Testing & Fast Rollback
- **Decision:** Execute `tests/deployment/smoke.py` post-deployment; automatically revert traffic on probe failure.
- **Status:** Approved & Implemented.

## FCD12-ADR-012: Least-Privilege CI Secret & Permission Model
- **Decision:** Restrict GitHub Actions token permissions to `contents: read` by default, isolating untrusted PRs from production credentials.
- **Status:** Approved & Implemented.
