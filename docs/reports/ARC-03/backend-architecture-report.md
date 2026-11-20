# ARC-03 Backend Architecture Report

**Document ID:** REP-ARC03-BE  
**Project:** ModularMenu / Menu-It  
**Governing Specification:** ARC-03 §4, §5, §6 (Backend Application Architecture)  
**Status:** Approved & Formally Verified  
**Audit Date:** 2026-11-20  

---

## 1. Overview & Architectural Pattern

The backend service is engineered as a **Modular Monolith** using **FastAPI** and **Python 3.12**.

In accordance with **ADR-0017 (ARC03-D05)** and **ARC-03 §4**, the backend implements a clean, layered architecture with strict inversion of control. Domain entities and business use cases remain completely decoupled from HTTP frameworks, database ORMs, and infrastructure drivers.

---

## 2. Layer Structure & Responsibilities

The backend is partitioned into four explicit layers:

```
backend/app/
├── api/                             # Layer 1: Presentation / HTTP Layer
│   └── v1/                          # Versioned REST Routers
│       ├── auth.py                  # Authentication & token endpoints
│       ├── restaurants.py           # Restaurant administrative endpoints
│       ├── menus.py                 # Menu & catalog endpoints
│       ├── themes.py                # Design token & theme endpoints
│       ├── publishing.py            # Immutable snapshot publication
│       └── public.py                # Public unauthenticated diner menu query
├── shared/
│   ├── domain/                      # Layer 3: Domain Layer (Pure Python)
│   │   ├── entities.py              # Pure domain models (MenuEntity)
│   │   └── exceptions.py            # Domain exceptions (DomainException, etc.)
│   ├── application/                 # Layer 2: Application Layer (Use Cases)
│   │   ├── commands.py              # Command & Result DTOs (CreateMenuCommand)
│   │   ├── interfaces.py            # Repository & UoW Protocols (MenuRepository)
│   │   └── use_cases.py             # Business workflows (CreateMenuUseCase)
│   └── infrastructure/              # Layer 4: Infrastructure Layer (Adapters)
│       └── repositories.py          # SQLAlchemy implementations & UoW
├── core/                            # Cross-cutting system core
│   ├── config.py                    # Pydantic Settings & deployment profiles
│   ├── errors.py                    # RFC 7807 exception handlers
│   ├── logging.py                   # Structured log formatting
│   ├── middleware.py                # CorrelationIdMiddleware & timing
│   └── security.py                  # JWT & Bcrypt password cryptography
├── db/                              # Relational database persistence
│   ├── base.py                      # SQLAlchemy declarative base
│   └── session.py                   # Async session maker & engine
├── models/                          # SQLAlchemy ORM entity models
├── bootstrap.py                     # Lifespan startup/shutdown orchestrator
└── main.py                          # Application factory (create_application)
```

---

## 3. Dependency Inversion & Protocols

To prevent tight coupling between business logic and database persistence:
1. **Abstract Protocols (`backend/app/shared/application/interfaces.py`):**
   - `MenuRepository`: Defines `get_by_id`, `get_by_slug`, `save`, and `delete`.
   - `UnitOfWork`: Defines async context manager interface (`__aenter__`, `__aexit__`) with `commit()` and `rollback()`.
2. **Domain Invariants (`backend/app/shared/domain/entities.py`):**
   - Pure Python dataclass `MenuEntity`.
   - Automatic invariant validation on instantiation:
     - Name must be between 1 and 255 characters.
     - Slug must conform strictly to `^[a-z0-9]+(?:-[a-z0-9]+)*$`.
3. **Application Use Case (`backend/app/shared/application/use_cases.py`):**
   - `CreateMenuUseCase` coordinates business logic across `MenuRepository` and `UnitOfWork`.
   - Checks slug uniqueness, instantiates `MenuEntity`, commits via `UnitOfWork`, and returns `MenuResult`.
4. **Concrete Adapter (`backend/app/shared/infrastructure/repositories.py`):**
   - `SqlAlchemyMenuRepository` implements `MenuRepository` using SQLAlchemy async sessions.
   - `SqlAlchemyUnitOfWork` implements `UnitOfWork` managing atomic database transactions.
5. **In-Memory Test Doubles (`tests/fixtures/fakes.py`):**
   - `InMemoryMenuRepository` and `InMemoryUnitOfWork` enable sub-millisecond unit testing without database or network I/O.

---

## 4. Application Lifecycle & Operational Probes

Per **ARC-03 §6.2**, the application separates liveness from readiness probes:
- `GET /health/live`: Returns `{"status": "ok", "process": "healthy"}` indicating the Python process is alive and responsive.
- `GET /health/ready`: Probes database connectivity (`SELECT 1`). Returns `{"status": "ready", "database": "connected"}` when operational, or `503 Service Unavailable` when the database is unreachable.
- `GET /health`: Backward-compatible legacy health check.

The application factory (`backend/app/main.py:create_application()`) utilizes the FastAPI `lifespan` context manager, delegating to `backend/app/bootstrap.py` for structured startup and graceful shutdown.

---

## 5. Middleware & Request Correlation

The `CorrelationIdMiddleware` (`backend/app/core/middleware.py`) intercepts every request:
1. Reads `X-Request-ID` header if supplied by client; generates a fresh `UUIDv4` string if absent.
2. Injects `request_id` into `request.state` and structured logging context.
3. Attaches `X-Request-ID` to all HTTP responses.
4. Calculates execution duration and attaches `X-Response-Time` header.
5. Integrates with RFC 7807 error handlers so that all 4xx/5xx responses include `request_id` in their JSON body.

---

## 6. Backend Verification Summary

The backend architecture satisfies all functional, structural, and non-functional requirements defined in ARC-03 WP-ARC03-03, WP-ARC03-04, and WP-ARC03-08.
