# FCD-12 · Document 13: Test Data & Environment Management

**Phase:** FCD-12 — Automated Testing & CI/CD Foundation  
**System:** Menu-It Restaurant SaaS Platform  
**Status:** Completed & Approved  
**Date:** 2026-11-26  

---

## 1. Test Isolation Rules

To eliminate flaky tests and race conditions:
1. **No Shared Mutable State:** Every integration test creates unique organization IDs, user accounts, and restaurant entities via factory fixtures.
2. **PostgreSQL Rollback Fixtures:** Database transactions in integration tests are rolled back after each test function completes.
3. **Synthetic PII Only:** All test user names, email addresses (`test-user-*@example.com`), and phone numbers are generated synthetically; real customer data is strictly forbidden in test environments.

---

## 2. Environment Matrix

| Environment | Purpose | Database | Caching |
| :--- | :--- | :--- | :--- |
| **Local** | Developer workstation | Local PostgreSQL or SQLite | Redis or in-memory |
| **CI** | Pull-request verification | Ephemeral PostgreSQL 16 container | In-memory fallback |
| **Staging** | Pre-production testing | Isolated cloud PostgreSQL RDS | Dedicated Redis cluster |
| **Production** | Live tenant traffic | High-availability PostgreSQL with PITR | High-availability Redis |
