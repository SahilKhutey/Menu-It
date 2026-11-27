# FCD-12 · Document 20: CI/CD Troubleshooting & Diagnostics Guide

**Phase:** FCD-12 — Automated Testing & CI/CD Foundation  
**System:** Menu-It Restaurant SaaS Platform  
**Status:** Completed & Approved  
**Date:** 2026-11-26  

---

## 1. Common Pipeline Failures & Diagnostic Steps

### 1. Backend Pytest Hangs or Times Out in CI
- **Cause:** Unclosed database connection pool or asyncio event loop mismatch.
- **Remedy:** Ensure test fixtures close engines via `await engine.dispose()`. Use `asyncio_default_fixture_loop_scope = "function"`.

### 2. Frontend Vitest or Next.js Build Fails with Out-of-Memory
- **Cause:** Default Node heap size exceeded during parallel Next.js page compilation.
- **Remedy:** Set `NODE_OPTIONS: "--max-old-space-size=4096"` in workflow environment variables.

### 3. Alembic Migration Fails with Multiple Heads
- **Cause:** Two feature branches added migrations independently.
- **Remedy:** Run `alembic merge -m "merge conflicting heads" head1 head2` or rebase the migration revision tree.

### 4. Flaky E2E Browser Tests
- **Cause:** Timing assertions failing before dynamic DOM rendering completes.
- **Remedy:** Avoid arbitrary sleeps; use Playwright web-first assertions (`await expect(locator).toBeVisible()`).
