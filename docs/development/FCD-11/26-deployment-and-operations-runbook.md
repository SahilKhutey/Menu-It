# FCD-11 · Document 26: Production Readiness, Deployment Runbooks & Operations Manual

**Phase:** FCD-11 — Security, Reliability & Observability Foundation  
**System:** Menu-It Restaurant SaaS Platform  
**Status:** Completed & Approved  
**Date:** 2026-11-26  

---

## 1. Production Release Checklist

Before releasing a new version of Menu-It to production, the release engineer must verify:

1. [x] **Alembic Head Verification:** `python -m alembic heads` matches expected head revision (`0008_security_audit_events`).
2. [x] **Environment Validation:** Production settings pass `ensure_production_config` without raising `SecurityConfigurationError`.
3. [x] **Quality Gates:** 100% automated tests pass (`python -m pytest`), `ruff check` reports zero errors, and `pnpm format:check` and `pnpm -r typecheck` pass cleanly.
4. [x] **Database Migration Execution:** Pre-deploy migration step completes successfully before routing traffic to new pods.
5. [x] **Telemetry & Probes:** Health probes (`/api/v1/health`, `/api/v1/health/database`) and `/api/v1/metrics` report 200 OK.

---

## 2. Zero-Downtime Deployment Procedure

1. Deploy new container image to Kubernetes cluster using a rolling update strategy (`maxSurge=25%`, `maxUnavailable=0`).
2. Readiness probe validates `/api/v1/health` and database connectivity before the pod receives traffic from the load balancer.
3. Old pods receive `SIGTERM`, enter graceful shutdown (`shutdown_runtime`), finish in-flight requests within a 30-second grace period, and terminate.
