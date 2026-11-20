# ARC-06 — Data Architecture

**ModularMenu Architecture Series · Version 1.0.0**  
**Status: Approved Baseline & Implemented**

---

## 1. Executive Summary

ARC-06 converts the domain boundaries (ARC-04) and tenant-isolation principles (ARC-05) into a concrete, production-grade relational persistence architecture for ModularMenu.

Key characteristics:
1. **Relational-First, Tenant-Aware:** Shared PostgreSQL database and schema for Managed SaaS, with 100% domain and schema parity for the Customer-Hosted Docker appliance.
2. **Organization-Based Ownership & Composite Keys:** Every tenant-owned record carries `organization_id`. Child branch entities carry both `organization_id` and `restaurant_id`, enforced by composite foreign keys `(organization_id, parent_id)`.
3. **Immutable Publication Snapshots:** Published menus are captured as immutable, SHA-256 verified JSON snapshots, protected by database and ORM event guards.
4. **Defense-in-Depth:** Application authorization, composite relational foreign keys, and PostgreSQL Row-Level Security (RLS) form three independent security tiers.
5. **Fixed-Precision Monetary Math:** Float values are strictly prohibited; prices use integer minor units or fixed-scale numeric types.

---

## 2. Document Map

| Document ID | Title | Summary |
|---|---|---|
| `01-data-architecture-overview.md` | Data Architecture Overview | Purpose, scope, architectural objectives DA-01 through DA-10 |
| `02-data-ownership-model.md` | Data Ownership Model | Global, organization, restaurant, and public read scopes |
| `03-entity-catalogue.md` | Entity Catalogue | Catalogue of entities across all 10 logical capability groups |
| `04-er-diagrams.md` | Entity-Relationship Diagrams | Mermaid ERDs illustrating relational hierarchies and composite links |
| `05-logical-data-model.md` | Logical Data Model | Domain entities, value objects, and cardinality rules |
| `06-physical-database-schema.md` | Physical Database Schema | Table definitions, DDL, column data types, and check constraints |
| `07-database-naming-standards.md` | Naming Standards | Conventions for tables, columns, PKs, FKs, UQs, CKs, and IXs |
| `08-tenant-data-integrity.md` | Tenant Data Integrity | Composite foreign key chains preventing cross-tenant attachment |
| `09-postgresql-rls-policies.md` | PostgreSQL RLS Policies | Row-Level Security policies, transaction-local settings, and roles |
| `10-sqlalchemy-persistence.md` | SQLAlchemy Persistence | Declarative Base, UUIDPrimaryKey, Timestamped mixins, and models |
| `11-repository-and-unit-of-work.md` | Repository & Unit of Work | Scoped repository patterns and asynchronous Unit of Work |
| `12-index-and-query-strategy.md` | Indexing & Query Strategy | Index design, EXPLAIN verification, pagination, and timeouts |
| `13-jsonb-configuration-strategy.md` | JSONB Configuration | Controlled JSONB use cases, validation, and schema versioning |
| `14-menu-snapshot-data-model.md` | Menu Snapshot Data Model | Snapshot structure, canonical SHA-256 serialization, immutability |
| `15-transaction-and-consistency.md` | Transactions & Consistency | Transaction boundaries, optimistic concurrency, outbox, idempotency |
| `16-migration-strategy.md` | Migration Strategy | Alembic setup, revision dependency order, and execution policy |
| `17-seed-and-reference-data.md` | Seed & Reference Data | Idempotent reference data seeding and separation from customer data |
| `18-data-lifecycle-and-retention.md` | Data Lifecycle & Retention | Resource state machines, deletion policies, and offboarding |
| `19-backup-and-restore.md` | Backup & Recovery | SaaS and customer-hosted backup, PITR, and recovery verification |
| `20-data-validation-rules.md` | Data Validation Rules | Multi-layer validation (UI, API/Pydantic, Domain, Database) |
| `21-data-testing-strategy.md` | Testing Strategy | Test environments, test harness, and 55-test scenario matrix |
| `22-verification-and-validation.md` | Verification & Validation | ARC06-VF01–VF12, validation scenarios VAL-01–VAL-07, release gate |
| `23-implementation-work-packages.md` | Work Packages | Implementation work packages WP-ARC06-01 through WP-ARC06-12 |
| `24-data-risk-register.md` | Data Risk Register | 16 data risks (ARC06-R01–R16) and enforceable mitigations |
| `25-architecture-decision-records.md` | Architecture Decisions | 25 approved decisions (ARC06-D01–D25 / ADR-0064–0088) |
| `26-architecture-compliance-report.md` | Compliance Report | Traceability matrix, sign-off criteria, and release approval |

---

## 3. Technical Artifacts

- **Manifests:**
  - `backend/architecture/data_ownership.yaml`
  - `backend/architecture/rls_coverage.yaml`
- **SQLAlchemy 2.x Declarative Models:**
  - `backend/app/shared/infrastructure/database/base.py`
  - `backend/app/infrastructure/database/models/` (identity, organizations, restaurants, menus, pricing, presentation, publishing, media, licensing, operations)
- **Unit of Work & Immutability:**
  - `backend/app/shared/infrastructure/database/unit_of_work.py`
  - `backend/app/shared/infrastructure/database/immutability.py`
- **Reference Data Seed Scripts:**
  - `backend/app/scripts/seed_reference_data.py`
- **Automated Verification:**
  - `tests/database/test_arc06_data_catalogue.py` (55 test scenarios passing)
