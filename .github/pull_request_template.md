## Pull Request Description

### Summary of Changes
<!-- Provide a concise description of the changes introduced in this PR -->

### Related Work & Governing References
- **FCD Milestone:** 
- **Work Package:** 
- **ADR Reference:** 
- **Issue / Ticket:** 

---

## Architectural & Security Compliance Checklist

### 1. Architectural & Multi-Tenancy Principles
- [ ] **Modularity & Boundaries:** Clean module boundary, no circular imports, explicit interfaces.
- [ ] **Dual-Layer Tenant Isolation:** All queries filter by `organization_id`; `assert_tenant_boundary` and PostgreSQL RLS verified.
- [ ] **Configuration-Driven:** Zero client-specific hardcoding, data-driven customizations.
- [ ] **Immutable Records:** Security audit events, idempotency, and published snapshots are append-only.
- [ ] **Precision & Safety:** Monetary values use Decimal/Numeric; UTC timezone-aware datetimes.

### 2. Quality & Verification Gates
- [ ] **Backend Unit & API Tests:** `python -m pytest apps/api/tests -v` (100% pass)
- [ ] **Backend Lint & Format:** `ruff check apps/api` & `ruff format --check apps/api` (zero errors)
- [ ] **Frontend Quality:** `pnpm format:check`, `pnpm -r typecheck`, and `pnpm -r lint` (100% pass)
- [ ] **Frontend Tests:** `pnpm test` (Vitest unit and component tests passing)
- [ ] **E2E Workflows:** `playwright test` passing on critical workflows

### 3. Database & Migrations
- [ ] No database schema changes
- [ ] Alembic migration added, single head verified (`alembic heads`), and tested forward/backward
- [ ] PostgreSQL Row-Level Security (RLS) policies enabled and tested
- [ ] Non-destructive expand-and-contract migration strategy verified

### 4. Security & Reliability Review
- [ ] No secrets, credentials, or private keys committed
- [ ] Sensitive fields redacted in logs and error responses (`redact_data`)
- [ ] Bounded timeouts and circuit breakers applied to remote calls
- [ ] Rate limits configured and verified

---

## Verification Evidence
<!-- Attach test results summary, coverage metrics, or relevant logs. -->

## Reviewer Sign-Off
- [ ] Architecture & Multi-Tenancy Verified
- [ ] Security & Compliance Gates Passed
- [ ] Approved for Merge
