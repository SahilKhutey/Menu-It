# FCD-12 · Document 03: Frontend Testing Infrastructure

**Phase:** FCD-12 — Automated Testing & CI/CD Foundation  
**System:** Menu-It Restaurant SaaS Platform  
**Status:** Completed & Approved  
**Date:** 2026-11-26  

---

## 1. Frontend Vitest Architecture

The frontend monorepo utilizes Vitest configured at root via `vitest.config.mjs`:
- Fast ESM-native execution across `@menu-it/web`, `@menu-it/admin`, and shared packages.
- Test discovery: `apps/*/tests/**/*.{test,spec}.{ts,tsx}` and `packages/*/tests/**/*.{test,spec}.{ts,tsx}`.
- Execution via workspace scripts: `pnpm test` delegates to `pnpm -r --if-present test`.

---

## 2. Test Suites

1. **`@menu-it/web`:** Validates API client error parsing, status code mappings, and error envelope handling.
2. **`@menu-it/admin`:** Validates administrative permission errors, session expiration behavior, and role guards.
3. **`@menu-it/theme-engine`:** Validates non-mutating deterministic deep merge of restaurant token overrides into base theme presets.

---

## 3. Frontend Execution Commands

```bash
# Run all frontend tests across workspace
pnpm test

# Run tests for specific application
pnpm --filter @menu-it/web test
pnpm --filter @menu-it/admin test

# Run typecheck and lint
pnpm -r typecheck
pnpm -r lint
```
