# 01 — Domain Architecture Overview

**Specification:** ARC-04 §4  
**Project:** ModularMenu  

---

## 1. Domain Capability Map

ModularMenu decomposes restaurant operations into five functional capability groups:

```mermaid
graph TD
    subgraph A ["A. Platform Foundation"]
        M01["MOD-01: Identity & Authentication"]
        M02["MOD-02: Tenant & Organization"]
        M03["MOD-03: Restaurant Management & Configuration"]
    end

    subgraph B ["B. Menu Business Domain"]
        M04["MOD-04: Menu Management"]
        M05["MOD-05: Category Management"]
        M06["MOD-06: Food Item Management"]
        M07["MOD-07: Pricing & Availability"]
        M14["MOD-14: Media Management"]
    end

    subgraph C ["C. Experience Configuration"]
        M08["MOD-08: Theme Engine"]
        M09["MOD-09: Layout Engine"]
        M10["MOD-10: Component Registry"]
        M12["MOD-12: Visual Menu Editor"]
    end

    subgraph D ["D. Delivery & Publication"]
        M11["MOD-11: Menu Rendering Engine"]
        M13["MOD-13: Publishing & Versioning"]
    end

    subgraph E ["E. Commercial & Operational Capabilities"]
        M15["MOD-15: Subscription & Licensing"]
        M16["MOD-16: Analytics & Integrations"]
    end

    M01 --> M02
    M02 --> M03
    M03 --> M04
    M04 --> M05
    M05 --> M06
    M06 --> M07
    M08 --> M11
    M09 --> M11
    M10 --> M11
    M13 --> M11
    M12 -.->|Drafts| M08
```

---

## 2. Core Architectural Principles
1. **Module Ownership:** Every capability has exactly one authoritative owner. No module exposes raw ORM models or database sessions across boundaries.
2. **Explicit Boundaries:** Modules communicate exclusively via typed Python Protocols and domain events.
3. **Domain-First Design:** Domain logic contains zero dependencies on HTTP frameworks (FastAPI), frontend libraries, or database drivers (SQLAlchemy).
4. **No Premature Microservices:** Modular monolith structure deployed in a unified container process.
