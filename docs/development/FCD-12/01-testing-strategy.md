# FCD-12 · Document 01: Testing Strategy & Quality Policy

**Phase:** FCD-12 — Automated Testing & CI/CD Foundation  
**System:** Menu-It Restaurant SaaS Platform  
**Status:** Completed & Approved  
**Date:** 2026-11-26  

---

## 1. Multi-Tier Testing Pyramid

Menu-It enforces quality across eight distinct verification levels:

```
                      ┌───────────────────────┐
                      │ L8: Production Smoke  │
                      ├───────────────────────┤
                      │ L7: Recovery & Chaos  │
                      ├───────────────────────┤
                      │ L6: Performance / k6  │
                      ├───────────────────────┤
                      │ L5: E2E / Playwright  │
                      ├───────────────────────┤
                      │ L4: API Contract Tests│
                      ├───────────────────────┤
                      │ L3: Database Integration │
                      ├───────────────────────┤
                      │ L2: Component Tests   │
                      ├───────────────────────┤
                      │ L1: Unit Tests (Fast) │
                      └───────────────────────┘
```

---

## 2. Quality Gate Policies & Thresholds

| Quality Gate | Acceptance Target | Enforcement Mechanism |
| :--- | :--- | :--- |
| **Formatting** | 100% compliant | `ruff format --check` and `prettier --check` |
| **Linting** | Zero errors | `ruff check` and `eslint` |
| **Static Typing** | Zero type errors | `tsc --noEmit` across all 6 workspace packages |
| **Backend Unit Tests** | 100% pass | `pytest tests/unit tests/security` |
| **Frontend Tests** | 100% pass | `pnpm test` via Vitest |
| **Database Migrations**| Single head revision, 100% pass | `alembic heads && alembic upgrade head` |
| **Security Audit** | Zero high/critical vulnerabilities | `pip-audit` & `pnpm audit --prod` |
| **Container Build** | Clean build from checkout | Multi-stage Docker build with non-root user |
| **Deployment Smoke**| 100% endpoints healthy | `tests/deployment/smoke.py` |
