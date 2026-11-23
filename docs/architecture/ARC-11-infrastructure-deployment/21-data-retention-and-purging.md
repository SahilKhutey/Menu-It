# 21 — Data Retention & Purging Policies
**ARC-11: Infrastructure & Deployment Architecture**

## 1. Retention Policies
- **Transactional Outbox Events:** Processed events retained for 14 days, then purged via automated cron worker.
- **Application Audit Logs:** Retained for 365 days in compressed archive storage.
- **Database Backups:** Daily snapshots (7 days), weekly snapshots (4 weeks), monthly snapshots (12 months).
- **Temporary Uploads:** Incomplete or orphaned media uploads cleaned up after 24 hours.\n