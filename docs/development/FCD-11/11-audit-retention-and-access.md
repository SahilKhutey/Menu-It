# FCD-11 · Document 11: Audit Log Retention, Immutability & Access Governance

**Phase:** FCD-11 — Security, Reliability & Observability Foundation  
**System:** Menu-It Restaurant SaaS Platform  
**Status:** Completed & Approved  
**Date:** 2026-11-26  

---

## 1. Immutability & Append-Only Guarantees

1. **No UPDATE or DELETE Privileges:**
   - Database application user accounts are granted `INSERT` and `SELECT` privileges only on `security_audit_events`.
   - `UPDATE` and `DELETE` privileges are strictly prohibited on the audit table.
2. **Audit Timestamp Integrity:**
   - `created_at` defaults to database `CURRENT_TIMESTAMP` and cannot be retroactively modified.
   - `occurred_at` requires a timezone-aware UTC datetime.

---

## 2. Retention & Archival Policies

- **Online Query Window:** 90 days of security audit events remain hot in PostgreSQL for operational queries and customer compliance reports.
- **Cold Storage Archival:** Events older than 90 days are partitioned and archived to immutable object storage (AWS S3 Glacier or Cloudflare R2) with WORM (Write Once, Read Many) policies enabled.
- **Total Retention Period:** 365 days (1 year) minimum for PCI-DSS and SOC 2 compliance.

---

## 3. Access Governance

- Tenant administrators can only inspect audit records where `organization_id == current_organization_id`.
- Platform security teams have read-only access for cross-tenant forensic investigations.
- Any query against `security_audit_events` itself emits an operational log entry tracking the auditor's identity.
