# FCD-08 §17 — Execution and Setup Guide

## 1. Prerequisites

- **Node.js:** `>= 18.17.0` (Recommended: Node 20 LTS)
- **Package Manager:** `pnpm@11.11.0` (or `pnpm >= 9.x`)
- **Python:** `>= 3.11` (for backend testing and runtime)

---

## 2. Installation & Development

### 2.1 Workspace Dependencies
Install and link all monorepo packages:
```bash
pnpm install
```

### 2.2 Running Development Servers
To start all services concurrently (FastAPI Backend, Next.js Web, Next.js Admin):
```bash
pnpm dev
```

Or start applications individually:
```bash
# Customer & Restaurant Web (Port 3000)
pnpm --filter @menu-it/web dev

# Platform Administration (Port 3001)
pnpm --filter @menu-it/admin dev

# Backend API (Port 8000)
pnpm dev:api
```

---

## 3. Verification & Quality Gates

Run the automated quality gates:
```bash
# Code formatting check
pnpm format:check

# TypeScript strict typechecking
pnpm -r typecheck

# Next.js and ESLint static analysis
pnpm -r lint

# Production bundle builds
pnpm --filter @menu-it/web build
pnpm --filter @menu-it/admin build

# Pytest backend test suite
python -m pytest apps/api/tests -q
```
