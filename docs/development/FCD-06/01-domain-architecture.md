# FCD-06 §01 — Domain Architecture & Boundaries

## 1. Executive Summary

Phase FCD-06 establishes the pure Domain Layer and Shared Business Foundation for Menu-It. Operating within a Modular Monolith architecture, the domain models represent the authoritative enterprise rules, entities, value objects, and business invariants governing restaurant software-as-a-service operations.

## 2. Architectural Positioning

The domain layer resides at the innermost core of the Menu-It backend architecture, strictly decoupled from frameworks, transport layers, database ORMs, and persistence mechanisms:

```
+-------------------------------------------------------------------+
|               Application Interfaces (FastAPI / Web)               |
+-------------------------------------------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
|          Application Services & Use Cases (menu_it.services)       |
+-------------------------------------------------------------------+
         |                                           |
         v (Uses Ports)                              v (Maps DTOs)
+-------------------------+             +---------------------------+
|      Domain Core        |             |   Shared API Contracts    |
| (menu_it.domain.*)      |             |   (menu_it.contracts.*)   |
|                         |             +---------------------------+
| - Entities & Aggregates |                           ^
| - Value Objects         |                           | (Mirror)
| - Domain Invariants     |             +---------------------------+
| - Domain Events         |             |   TypeScript Contracts    |
| - Repository Ports      |             |  (@menu-it/shared-types)  |
+-------------------------+             +---------------------------+
         ^
         | (Implements Ports)
+-------------------------------------------------------------------+
|      Infrastructure & Adapters (SQLAlchemy, PostgreSQL, RLS)       |
+-------------------------------------------------------------------+
```

## 3. Strict Boundary Rules

1. **Zero External Framework Dependencies**:
   `menu_it.domain` has **zero imports** of `fastapi`, `sqlalchemy`, `pydantic`, or any database session object. It depends solely on the Python Standard Library (`dataclasses`, `datetime`, `decimal`, `uuid`, `zoneinfo`, `enum`) and standard parsing utilities (`phonenumbers`).

2. **Inverted Dependencies (Ports & Adapters)**:
   The domain specifies its persistence, transaction, and messaging requirements via structural interfaces (Protocols) in `menu_it.domain.ports`. Infrastructure adapters in `menu_it.infrastructure` implement these ports.

3. **Domain Purity & Invariants**:
   Every domain entity and value object protects its internal state. Invalid state transitions, malformed currency operations, or overlapping operating hours are rejected at instantiation or mutation via domain exception hierarchies (`DomainError`).
