## Pull Request Description

### Summary of Changes
<!-- Provide a concise description of the changes introduced in this PR -->

### Governing Architecture & ADR Reference
- [ ] Conforms to **ARC-01** (System Architecture Overview)
- [ ] Conforms to **ARC-02** (Principles, Standards & Constraints)
- [ ] Relevant ADR: `ADR-XXXX` (or link to approved architecture issue)

---

## Architectural Compliance Checklist

### 1. Architectural Principles
- [ ] **P-01 (Modularity):** Clean module boundary, no circular dependencies, explicit public interfaces.
- [ ] **P-02 (Separation of Concerns):** No database/infrastructure logic in domain layers.
- [ ] **P-03 (Configuration-Driven):** No client-specific code forks, custom CSS overrides, or visual hardcoding.
- [ ] **P-04 (Multi-Tenant Isolation):** All tenant data filtered explicitly by `restaurant_id`; tenant isolation tests pass.
- [ ] **P-05 (Content/Theme Decoupling):** Menu catalog changes do not touch themes; theme changes do not touch dishes.
- [ ] **P-07 (Immutable Publishing):** Published snapshots remain immutable with SHA-256 hashes.
- [ ] **P-08 (Deployment Portability):** Verified compatible across both Managed SaaS and Self-Hosted Docker profiles.
- [ ] **P-09 (Secure by Design):** AuthN/AuthZ enforced; no plaintext credentials or API keys committed.

### 2. Constraints & Quality Gates
- [ ] No synchronous relational joins on public diner endpoints (`/api/v1/public/...`).
- [ ] Monetary attributes use fixed-precision `Numeric(12,2)` / minor units (no `float`).
- [ ] All timestamps are in UTC with explicit timezone offsets.
- [ ] SQLAlchemy relationships explicitly define `lazy="raise"` or explicit join strategies.
- [ ] API errors adhere to RFC 7807 problem details specification.

---

## Testing & Verification
- [ ] Unit tests added / passing (`pytest tests/unit`)
- [ ] Integration & isolation tests passing (`pytest tests/integration tests/security`)
- [ ] Architecture boundary tests passing (`pytest tests/architecture`)
- [ ] Frontend type check and build passing (`pnpm run build` or `npm run build`)
- [ ] Linter and formatters clean (`ruff check .`, `ruff format --check .`)

---

## Reviewer Sign-Off
- [ ] Architecture Compliance Verified
- [ ] Security & Tenancy Verified
- [ ] Approved for Merge
