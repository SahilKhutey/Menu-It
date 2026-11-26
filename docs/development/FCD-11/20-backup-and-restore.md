# FCD-11 · Document 20: Database Backup Strategies, Automation & Verification

**Phase:** FCD-11 — Security, Reliability & Observability Foundation  
**System:** Menu-It Restaurant SaaS Platform  
**Status:** Completed & Approved  
**Date:** 2026-11-26  

---

## 1. Backup Strategy & Objectives

The Menu-It database backup policy ensures business continuity and data protection against corruption, hardware failure, and accidental deletion:

- **Recovery Point Objective (RPO):** Maximum 15 minutes of potential data loss.
- **Recovery Time Objective (RTO):** Maximum 4 hours to complete full database restoration and integrity verification.

---

## 2. Backup Tiers & Automation

1. **Continuous WAL Archiving (Point-in-Time Recovery):**
   - PostgreSQL Write-Ahead Logs (WAL) are streamed continuously to redundant cloud object storage (AWS S3 / GCS).
   - Allows point-in-time recovery (PITR) to any second within the retention window.
2. **Daily Full Physical Snapshots:**
   - Automated storage-level snapshots executed daily during low-traffic windows (02:00 UTC).
   - Encrypted with AES-256 via dedicated cloud KMS keys.
3. **Weekly Logical Dumps:**
   - Compressed `pg_dump` backups executed weekly to verify schema integrity and support table-level granular extraction.

---

## 3. Automated Restore Verification

- Backups are only valid if proven restorable.
- A scheduled weekly automated job restores the latest snapshot into an isolated sandbox environment, runs Alembic migration checks, executes smoke queries across tenant boundaries, and records a verification report.
