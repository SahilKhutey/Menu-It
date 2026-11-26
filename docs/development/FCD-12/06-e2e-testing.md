# FCD-12 · Document 06: End-to-End (E2E) Testing Architecture

**Phase:** FCD-12 — Automated Testing & CI/CD Foundation  
**System:** Menu-It Restaurant SaaS Platform  
**Status:** Completed & Approved  
**Date:** 2026-11-26  

---

## 1. Playwright Architecture

Menu-It implements end-to-end browser testing using Playwright (`playwright.config.ts` and `tests/e2e/critical-flows.spec.ts`):
- Cross-browser execution (Chromium engine in CI).
- Tests critical customer and administrative user journeys:
  - Public restaurant menu browsing and category navigation.
  - Handling of non-existent or unpublished restaurants (404/not found states).
  - Admin login and unauthenticated route redirection.
  - Multi-tenant boundary protection: preventing client manipulation of organization identifiers.

---

## 2. Test Execution

```bash
# Install browsers (local workstation)
pnpm exec playwright install --with-deps chromium

# Run E2E test suite
pnpm exec playwright test
```
