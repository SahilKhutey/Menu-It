# FCD-10 — Local Development & Developer Environment Guide

**Milestone:** `v1.0.0-fcd10`  
**Phase:** FCD-10 — Caching, Background Jobs & Event Infrastructure  
**Author:** AI Architecture & Core Engineering Team  
**Status:** Approved  

---

## 1. Local Prerequisites & Services

1. **Redis Server:**
   ```powershell
   # Run via Docker
   docker run --name menu-it-redis -p 6379:6379 -d redis:7-alpine
   ```
2. **FastAPI Backend Server:**
   ```powershell
   cd apps/api
   python -m uvicorn menu_it.main:app --host 127.0.0.1 --port 8000 --reload
   ```
3. **Background Worker Process:**
   ```powershell
   cd apps/api
   python -m arq menu_it.platform.jobs.worker.WorkerSettings
   ```

---

## 2. Verification Commands

```powershell
# Run backend tests
python -m pytest apps/api/tests -q

# Format check
pnpm format:check

# TypeScript typecheck
pnpm -r typecheck

# Lint check
pnpm -r lint
```
