# 25 — Architecture Decisions (ADR-0064 through ADR-0088)

## 1. Summary of Decisions (ARC06-D01 – ARC06-D25)

- **ADR-0064 (ARC06-D01):** PostgreSQL as the primary relational database.
- **ADR-0065 (ARC06-D02):** Shared logical schema for managed SaaS.
- **ADR-0066 (ARC06-D03):** UUIDv4 primary identifiers.
- **ADR-0067 (ARC06-D04):** Organization-level tenant ownership.
- **ADR-0068 (ARC06-D05):** Restaurant as subordinate resource to organization.
- **ADR-0069 (ARC06-D06):** Explicit `organization_id` on all tenant-owned records.
- **ADR-0070 (ARC06-D07):** Explicit `restaurant_id` on restaurant-scoped records.
- **ADR-0071 (ARC06-D08):** Composite foreign keys for tenant-owned relationships.
- **ADR-0072 (ARC06-D09):** SQLAlchemy 2.x ORM baseline.
- **ADR-0073 (ARC06-D10):** Alembic migration system.
- **ADR-0074 (ARC06-D11):** Controlled, versioned JSONB configuration.
- **ADR-0075 (ARC06-D12):** Integer minor units / Decimal monetary representation.
- **ADR-0076 (ARC06-D13):** UTC `TIMESTAMPTZ` for all temporal attributes.
- **ADR-0077 (ARC06-D14):** Application authorization + PostgreSQL RLS.
- **ADR-0078 (ARC06-D15):** Transaction-local PostgreSQL tenant context.
- **ADR-0079 (ARC06-D16):** Immutable menu publication snapshots.
- **ADR-0080 (ARC06-D17):** Tenant-scoped repository methods.
- **ADR-0081 (ARC06-D18):** Application-use-case transaction boundaries.
- **ADR-0082 (ARC06-D19):** Optimistic concurrency via `row_version`.
- **ADR-0083 (ARC06-D20):** Transactional outbox pattern for reliable events.
- **ADR-0084 (ARC06-D21):** Controlled data deletion and retention lifecycle.
- **ADR-0085 (ARC06-D22):** Published snapshot public read model.
- **ADR-0086 (ARC06-D23):** Object storage for media bytes, PostgreSQL for metadata.
- **ADR-0087 (ARC06-D24):** Tested database and media recovery procedures.
- **ADR-0088 (ARC06-D25):** 100% schema and binary parity across SaaS and customer-hosted editions.
