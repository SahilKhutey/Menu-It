# Backup Policy & Disaster Recovery Objectives
**ModularMenu Operational Documentation**

## 1. Service Level Objectives
- **Recovery Point Objective (RPO):** <= 1 hour. Maximum allowable data loss in catastrophic disaster is 1 hour.
- **Recovery Time Objective (RTO):** <= 4 hours. Complete system restoration must finish within 4 hours.

## 2. Backup Schedules
- Full Database Dump (`pg_dump`): Daily at 02:00 UTC.
- Hourly Differential / WAL Archiving: Every 60 minutes.
- Media Storage Sync: Continuous S3 cross-region replication or daily rsync snapshot.

## 3. Retention Tiers
- Daily backups: 7 days.
- Weekly backups: 4 weeks.
- Monthly backups: 12 months.\n