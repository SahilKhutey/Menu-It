# FCD-03 — Database Architecture & Data Access Foundation

## 1. Architectural Overview

Phase **FCD-03** establishes the persistent relational data layer for the **Menu-It** multi-tenant SaaS platform. It transforms the application skeleton established in FCD-02 into a database-backed system with versioned schemas, connection pooling, request-scoped sessions, repository isolation, and atomic transaction boundaries.

```mermaid
flowchart TD
    subgraph Client["Client Requests"]
        REQ["HTTP Requests"]
    end

    subgraph API["FastAPI Application (apps/api)"]
        EP["FastAPI Endpoints\n(/api/v1/...)"]
        DEP["Session Dependency\n(get_db_session)"]
    end

    subgraph Services["Application Services Layer"]
        SVC["Application Services\n(e.g., TenantService)"]
        TX["Transaction Boundary\n(session.begin())"]
    end

    subgraph Repositories["Data Access Layer"]
        REPO_B["BaseRepository[T]"]
        REPO_T["TenantRepository"]
        REPO_R["RestaurantRepository"]
    end

    subgraph ORM["SQLAlchemy 2.x Async Engine"]
        SESS["AsyncSession (Request-Scoped)"]
        POOL["Connection Pool (pool_size=5, max_overflow=10)"]
    end

    subgraph DB["PostgreSQL 17"]
        PG[("PostgreSQL Database\n(menu_it)")]
    end

    subgraph Migrations["Schema Versioning"]
        ALEMBIC["Alembic CLI / Migrations"]
    end

    REQ --> EP
    EP --> DEP
    DEP --> SESS
    EP --> SVC
    SVC --> TX
    TX --> SESS
    SVC --> REPO_T
    SVC --> REPO_R
    REPO_T -.-> REPO_B
    REPO_R -.-> REPO_B
    REPO_B --> SESS
    SESS --> POOL
    POOL --> PG
    ALEMBIC --> PG
```

---

## 2. Layer Responsibilities & Invariants

| Layer | Responsibility | Invariants & Exclusions |
| :--- | :--- | :--- |
| **FastAPI Endpoints** | HTTP routing, request parsing, response formatting. | No SQL construction; no direct repository creation without dependency injection. |
| **Application Services** | Orchestrates business workflows, coordinates multi-repository operations, owns transaction boundaries. | Services own `session.begin()`; translates lower-level database exceptions into sanitized domain exceptions. |
| **Repositories** | Encapsulates SQL queries, pagination, filtering, persistence, and deletion. | **Never commits** (`session.commit()` is forbidden); never creates engines or independent sessions. Calls `session.flush()`. |
| **AsyncSession** | Unit of work for database connections within a request lifecycle. | Strictly request-scoped via `get_db_session()`. Automatically disposed/closed upon request completion. |
| **Engine & Pool** | Connection acquisition, pre-ping validation, connection recycling, timeout management. | Application-global singleton managed through `apps/api/src/menu_it/database/engine.py`. Disposed on app shutdown. |
| **PostgreSQL 17** | Relational data persistence, foreign key enforcement, index management, constraints. | Authoritative source of data integrity and uniqueness. |
| **Alembic** | Version-controlled, reproducible schema migrations. | Sole approved mechanism for structural database schema changes in production. |

---

## 3. Request Execution Flow

```mermaid
sequenceDiagram
    autonumber
    actor Client
    participant API as FastAPI Endpoint
    participant Lifespan as get_db_session()
    participant Service as TenantService
    participant Repo as Repositories
    participant DB as PostgreSQL 17

    Client->>API: POST /api/v1/...
    API->>Lifespan: Acquire Request Session
    Lifespan-->>API: AsyncSession
    API->>Service: invoke operation(session, params)
    activate Service
    Service->>Service: async with session.begin()
    Service->>Repo: query / create entities(session)
    Repo->>DB: SQL SELECT / INSERT / flush
    alt Business Operation Succeeds
        Service-->>API: return domain entities
        Service->>DB: Atomic COMMIT
    else Constraint / Integrity Failure
        DB-->>Repo: IntegrityError
        Repo-->>Service: Exception
        Service->>DB: Automatic ROLLBACK
        Service-->>API: raise ResourceConflictError
    end
    deactivate Service
    API->>Lifespan: Request Completes -> Close Session
    Lifespan->>DB: Return connection to pool
    API-->>Client: HTTP JSON Response (Enveloped / Sanitized)
```
