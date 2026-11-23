# 12 — Backup & Disaster Recovery
**ARC-11: Infrastructure & Deployment Architecture**

## 1. Service Level Objectives (SLOs)
- **Recovery Point Objective (RPO):** <= 1 hour (daily full backups + hourly WAL archiving / differentials).
- **Recovery Time Objective (RTO):** <= 4 hours to complete full system recovery.

## 2. Backup Procedures
- Automated `pg_dump` with gzip compression and SHA-256 checksum verification (`infrastructure/scripts/backup-postgres.sh`).
- AES-256 encryption using GPG keys before off-host upload.
- Retention: 7 daily snapshots, 4 weekly snapshots, 12 monthly snapshots.
- Restoration drills conducted semi-annually (`infrastructure/scripts/restore-postgres.sh`).\n