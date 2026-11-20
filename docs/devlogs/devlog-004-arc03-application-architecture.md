# Devlog-004: ARC-03 Application Architecture & Technology Boundaries
**Date:** 2026-11-20  
**Milestone:** ARC-03 Application Architecture  
**Git Tag:** `v1.0.0-arc03`  
**Status:** Approved & Implemented  
**Author:** ModularMenu Architecture Team  

---

## 1. Application Topology: Modular Monolith

ARC-03 defines the software architecture of ModularMenu as a **modular monolith**:
- **Backend:** Python 3.12 with FastAPI for high-performance async I/O.
- **Frontend:** Next.js 14 with React 18, TypeScript 5, and Tailwind CSS.
- **Decoupled Lifecycle:** Separate frontend and backend deployment units communicating strictly via versioned REST APIs (`/api/v1/`).

---

## 2. Layered Architecture & Dependency Inversion

The backend enforces 4 strict structural layers:
```
[ API Layer ]         --> Routers, middleware, request parsing, response formatting
       │
       ▼
[ Application Layer ] --> Use cases, DTOs, orchestrators, transaction boundaries
       │
       ▼
[ Domain Layer ]      --> Pure business entities, aggregates, domain events, protocols
       │
       ▼
[ Infrastructure ]    --> Persistence adapters, database sessions, external integrations
```
- **Rule:** Dependencies point inwards. Domain models import zero external frameworks (no FastAPI, no SQLAlchemy).
- **Inversion of Control:** Repositories and Unit of Work defined as abstract Python `Protocol` interfaces in the application/domain layer, implemented in infrastructure.

---

## 3. Verification & Quality Gates

- **Performance Budget:** First Load JS for `/r/[slug]` route compiled to **95.2 kB** (well within the 120 kB budget).
- **Request Correlation:** `CorrelationIdMiddleware` injecting `X-Request-ID` and `X-Response-Time` headers on all responses.
- **Operational Probes:** Implemented `/health/live` and `/health/ready` endpoints.
- **Test Matrix:** 46 passing tests verified.
- **Decision Records:** `ADR-0013` through `ADR-0027` recorded in `docs/decisions/decision-register.md`.
