# 03 — Tenancy Isolation Model

## 1. Architectural Strategy: Shared Database, Shared Schema

For Managed SaaS, ModularMenu utilizes a **shared PostgreSQL database with a shared schema**, using composite relational keys and PostgreSQL Row-Level Security (RLS) for defense-in-depth.

### Comparison Matrix

| Isolation Strategy | SaaS Resource Efficiency | Operational Simplicity | Blast Radius Control | Selected Model |
|---|---|---|---|---|
| Separate Database per Tenant | Low (High cost overhead) | High DB count, complex migrations | Complete DB boundary | Customer-Hosted Only |
| Separate Schema per Tenant | Medium (Schema bloat) | Complex migration loops | Schema boundary | Rejected |
| Shared Database & Shared Schema | **Optimal (High density)** | **Unified migration path** | **PostgreSQL RLS + Composite FKs** | **Selected SaaS Baseline** |

## 2. Invariants

- Every tenant table has an `organization_id` column indexed with B-tree.
- Every tenant query binds `organization_id`.
- PostgreSQL RLS enforces `organization_id = NULLIF(current_setting('app.current_organization_id', true), '')::uuid`.
- Missing context fails closed (0 rows returned).
