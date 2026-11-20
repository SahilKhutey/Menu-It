# 01 — Data Architecture Overview

## 1. Purpose

ARC-06 converts the domain boundaries and tenant-isolation principles established in ARC-04 and ARC-05 into a concrete, unified data architecture.

It defines how ModularMenu stores, relates, validates, retrieves, migrates, protects, backs up and eventually deletes data across both deployment editions:
1. **Managed SaaS:** Shared PostgreSQL database and schema with organization-level tenant isolation.
2. **Customer-Hosted:** The identical schema and data rules deployed within the customer's private Docker infrastructure.

## 2. Core Architectural Objectives

- **DA-01 (Tenant Ownership):** Every private tenant-owned record has explicit organization ownership.
- **DA-02 (Referential Integrity):** Invalid or cross-tenant relationships are rejected by database composite foreign keys.
- **DA-03 (Data Consistency):** Business invariants are enforced at the database, domain, and API levels.
- **DA-04 (Query Efficiency):** Common application queries utilize deliberate composite B-tree indexes.
- **DA-05 (Data Security):** Tenant isolation is enforced via application authorization and PostgreSQL RLS.
- **DA-06 (Publication Integrity):** Published menu versions are immutable, SHA-256 verified snapshots.
- **DA-07 (Extensibility):** New modules introduce data without destabilizing existing schemas.
- **DA-08 (Portability):** Single binary/schema portability across SaaS and customer-hosted editions.
- **DA-09 (Recoverability):** Repeatable, tested backup, restore, and migration procedures.
- **DA-10 (Traceability):** Critical data modifications are attributed to actors via audit trails.
