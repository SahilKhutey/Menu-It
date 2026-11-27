# FCD-02 — Application Runtime Architecture

## 1. Purpose
Establish the runtime architecture and operational boundaries of the three independent application processes comprising Menu-It.

## 2. Applications
1. **Customer Web Application (`apps/web`):** Next.js 14 App Router, customer-facing discovery, menu presentation, and dining experience. Port 3000.
2. **Platform Administration Application (`apps/admin`):** Next.js 14 App Router, platform operations console, system oversight, tenant management. Port 3001.
3. **Backend API (`apps/api`):** Python 3.12 + FastAPI + Uvicorn modular monolith API runtime. Port 8000.

## 3. Runtime Technologies
- **Next.js & React 18:** Server and Client component rendering, responsive UI shell.
- **TypeScript:** Strict type checking (`strict: true`) across web, admin, and contracts.
- **Python 3.12 & FastAPI:** High-performance async ASGI REST API foundation.
- **Uvicorn:** Production-grade ASGI server implementation.

## 4. Application Boundaries
- Each application operates as an independent OS process with dedicated port allocations.
- Backend API owns all domain logic, lifecycle orchestration, and data security.
- Frontend shells communicate exclusively via versioned HTTP REST APIs (`/api/v1/*`).
- Shared contracts (`packages/shared-types`) ensure type-safe frontend-to-backend parity without leaking Python internals or backend database drivers.

## 5. Runtime Ports
- Customer Web: `http://localhost:3000`
- Platform Admin: `http://localhost:3001`
- Backend API: `http://localhost:8000`
- API Interactive Docs: `http://localhost:8000/api/v1/docs`

## 6. Runtime Lifecycle
The runtime adheres to strict phases: configuration loading, application factory instantiation, middleware registration, ASGI lifespan initialization, request acceptance, operational health monitoring, and graceful termination.

## 7. Mobile Readiness
Both frontend applications provide responsive foundations adhering to fluid layouts (320px to 1440px+), safe-area insets, and PWA manifest installability. Native applications remain separate future architectural decisions.
