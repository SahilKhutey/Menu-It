# FCD-02 — Menu-It Application Execution Guide

## 1. Prerequisites
- **Node.js:** v20+ / v24 LTS
- **pnpm:** v11+
- **Python:** 3.12+
- **Docker Desktop:** (Optional for local PostgreSQL)

## 2. Installation
```powershell
# Install all workspace dependencies
pnpm install
```

## 3. Individual Application Execution
```powershell
# Terminal 1 — Start Backend API (Port 8000)
pnpm dev:api

# Terminal 2 — Start Customer Web (Port 3000)
pnpm dev:web

# Terminal 3 — Start Platform Admin (Port 3001)
pnpm dev:admin
```

## 4. Unified Process Orchestration
Start all three processes concurrently with synchronized lifecycle termination:
```powershell
pnpm dev

# Or via automated PowerShell script:
powershell -ExecutionPolicy Bypass -File scripts/development/start-all.ps1
```

## 5. Verification Commands
```powershell
# Backend automated validation
powershell -ExecutionPolicy Bypass -File scripts/development/backend-check.ps1

# Frontend typechecking
pnpm -r --if-present typecheck

# Frontend linting
pnpm -r --if-present lint

# Code formatting check
pnpm format:check

# Production builds
pnpm --filter @menu-it/web build
pnpm --filter @menu-it/admin build
```

## 6. Process Teardown
Press `Ctrl+C` in the parent terminal. The `-k` flag terminates child processes concurrently.
To verify no orphaned ports:
```powershell
Get-NetTCPConnection -State Listen | Where-Object { $_.LocalPort -in @(3000, 3001, 8000) }
```
