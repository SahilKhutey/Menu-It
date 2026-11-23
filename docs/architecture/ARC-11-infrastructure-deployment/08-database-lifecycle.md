# 08 — Database Lifecycle & Migrations
**ARC-11: Infrastructure & Deployment Architecture**

## 1. Database Specifications
- **Engine:** PostgreSQL 16.
- **Extensions:** `uuid-ossp`, `pgcrypto`.
- **Multi-Tenancy:** Row-Level Security (RLS) policies on tenant-owned tables (`organization_id`).

## 2. Zero-Downtime Migration Protocol (Expand-and-Contract)
1. **Expand Phase:** Add nullable columns, new tables, or non-destructive triggers. Existing code operates without interruption.
2. **Deploy Phase:** Deploy new backend code that reads/writes both old and new schema elements.
3. **Contract Phase:** Backfill historical data, add `NOT NULL` constraints, remove deprecated columns.

## 3. Pre-Migration Safeguards (ARC11-I06)
Before applying any migration (`infrastructure/scripts/migrate.sh`), an automated `pg_dump` snapshot is taken and verified. If migration fails, the database is restored automatically.\n