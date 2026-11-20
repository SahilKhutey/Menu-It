# Devlog-007: ARC-06 Data Architecture & Persistence Baseline
**Date:** 2026-11-20  
**Milestone:** ARC-06 Data Architecture & Persistence Baseline  
**Git Tag:** `v1.0.0-arc06`  
**Status:** Approved & Implemented  
**Author:** ModularMenu Architecture Team  

---

## 1. Objectives & Persistence Strategy

ARC-06 converts the domain models and multi-tenancy rules from ARC-04 and ARC-05 into a concrete, relational-first persistence architecture:
- Shared logical PostgreSQL database and schema for Managed SaaS.
- Identical schema deployed in Customer-Hosted container environments.
- Relational rigor for core domain relationships, paired with versioned JSONB configurations for styling and immutable publication snapshots.

---

## 2. Composite Foreign Keys & Ownership Integrity

To enforce tenant boundaries directly at the database engine level, ARC-06 mandates composite foreign keys across all child relationships:
```sql
-- Category belongs to menu and must share the same organization
FOREIGN KEY (organization_id, menu_id) 
  REFERENCES menus (organization_id, id) ON DELETE CASCADE

-- Item belongs to category and must share the same organization
FOREIGN KEY (organization_id, category_id) 
  REFERENCES menu_categories (organization_id, id) ON DELETE CASCADE
```
- **Guaranteed Invariant:** Cross-tenant entity attachment (e.g., attaching an item in Org A to a category in Org B) is rejected by the database foreign key constraint, even if application logic fails.

---

## 3. SQLAlchemy 2.x Declarative Models Catalogue

Implemented 30+ declarative models across 10 functional groups in [`backend/app/infrastructure/database/models/`](file:///c:/Users/ASUS/Documents/Menu-it/backend/app/infrastructure/database/models/):
- **Base Infrastructure:** Standardized naming conventions (`ix_`, `uq_`, `ck_`, `fk_`, `pk_`), `UUIDPrimaryKey`, `Timestamped`, `TenantScoped`, and `RestaurantScoped` mixins.
- **Pricing & Minor Units:** Monetary values stored as integer minor units (`amount_minor`) or exact `NUMERIC(12,2)`. Floating point types are prohibited.
- **Partial Unique Indexes:** `uq_item_prices_default_per_item` ensures only one default price exists per item.
- **Optimistic Concurrency:** `row_version` integer column incremented on every draft modification.

---

## 4. Immutable Publication Snapshots

- **Snapshot Storage:** `menu_versions` table stores the frozen menu JSON payload, metadata, and canonical SHA-256 digest.
- **Mutation Guards:** Python ORM event listeners (`before_update`, `before_delete`) registered via [immutability.py](file:///c:/Users/ASUS/Documents/Menu-it/backend/app/shared/infrastructure/database/immutability.py) raise `ImmutableRecordMutationException` upon any modification attempt.
- **Publication Pointer:** `publications` table points to the active `menu_version_id` for each restaurant menu. Rollbacks update the pointer in <5ms without re-compilation.

---

## 5. Verification, Quality Gates & Release

- **55-Test Data Catalogue (ARC06-T001 to ARC06-T055):** Tested composite FK enforcement, duplicate slug rejection, partial index guarantees, JSONB validation, snapshot immutability, optimistic locking, and reference data seeding.
- **Total Backend Tests:** **199 passed** (100% pass rate in 9.68s).
- **Frontend Health:** Route `/r/[slug]` compiled to **95.2 kB** First Load JS (<120 kB ceiling).
- **Documentation Suite:** 27 comprehensive architectural documents generated in `docs/architecture/ARC-06-data-architecture/`.
- **Decision Records:** `ADR-0064` through `ADR-0088` recorded in `docs/decisions/decision-register.md`.
- **Release:** Tagged `v1.0.0-arc06` and pushed to GitHub repository.
