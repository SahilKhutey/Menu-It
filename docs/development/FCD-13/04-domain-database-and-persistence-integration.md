# FCD-13 · Document 04 — Domain, Database & Persistence Integration

## 1. Objective
Validates that domain models, value objects, SQLAlchemy ORM entities, repositories, PostgreSQL schemas, and the Transactional Outbox represent identical business concepts and maintain absolute transactional integrity.

---

## 2. Persistence Integration Architecture

```
Application Command / Service
  │
  ├──> Enforce Domain Invariants (Money, TimeZone, OperatingHours)
  │
  ├──> Execute Repository Port (SQLAlchemy Session)
  │      │
  │      ├──> Insert / Update Business Record
  │      └──> Insert Outbox Event (EventOutboxModel)
  │
  └──> Atomic Session Commit (or Rollback together)
```

---

## 3. Core Persistence Invariants

1. **Transactional Outbox Atomicity:**
   - Any domain event requiring durable external processing is staged in `event_outbox` within the exact same database transaction as the business entity mutation via `OutboxEventPublisher`.
   - If the business transaction rolls back, the outbox event is also discarded, eliminating ghost events.
2. **Monetary Precision:**
   - Currency arithmetic uses Python `Decimal` and explicit `Currency` value objects.
   - Binary floating-point arithmetic is strictly prohibited across money operations.
3. **UTC Timestamp Preservation:**
   - All persistence and domain timestamps are UTC-aware ISO8601 instants without timezone truncation.
4. **Composite Tenant Keys:**
   - Foreign keys to tenant resources incorporate `organization_id` to guarantee database-enforced multi-tenant referential integrity.

---

## 4. Integration Verification Matrix

| Test ID | Scenario | Expected Result | Verification Status |
| :--- | :--- | :--- | :---: |
| `DATAINT-T01` | Value object domain validation | Invalid values rejected before reaching repository | **PASSED** |
| `DATAINT-T02` | Outbox event serialization | `EventEnvelope` encapsulates tenant, actor, and payload | **PASSED** |
| `DATAINT-T03` | Monetary precision calculation | Exact decimal summation and multiplication | **PASSED** |
| `DATAINT-T04` | UTC timestamp handling | UTC offset preserved through serialization | **PASSED** |
| `DATAINT-T05` | Alembic single-head schema | Migrations 0001 through 0008 verified linear | **PASSED** |
| `DATAINT-T06` | Outbox transaction atomicity | Outbox record flushed within active session | **PASSED** |

---

## 5. Verification Evidence
Verified by:
- `apps/api/tests/integration/test_persistence_and_outbox_integration.py`
- Alembic linear revision history: `0001_create_foundational_tenant_and_restaurant_tables` to `0008_create_security_audit_events`.
