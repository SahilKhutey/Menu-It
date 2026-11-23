# 32 — Runbook & Operations Index
**ARC-11: Infrastructure & Deployment Architecture**

## Complete Directory of Operational Documentation
### Deployment Guides (`docs/deployment/`)
- `LOCAL_SETUP.md`: Developer workstation environment provisioning.
- `DEVELOPMENT_DEPLOYMENT.md`: Continuous staging deployment workflow.
- `STAGING_DEPLOYMENT.md`: Pre-production validation environment.
- `PRODUCTION_DEPLOYMENT.md`: Managed SaaS production release procedure.
- `CUSTOMER_HOSTED_INSTALLATION.md`: Customer on-premise installation guide.
- `CUSTOMER_HOSTED_UPGRADE.md`: Upgrade procedure for customer hosts.
- `RELEASE_CHECKLIST.md`: Pre-release verification gates.

### Operations Guides (`docs/operations/`)
- `SERVICE_OPERATIONS.md`: Container lifecycle, start/stop/restart routines.
- `DATABASE_OPERATIONS.md`: Maintenance, indexing, and connection management.
- `WORKER_OPERATIONS.md`: Outbox monitoring and DLQ reprocessing.
- `STORAGE_OPERATIONS.md`: Media bucket and directory maintenance.
- `MONITORING_GUIDE.md`: Telemetry, health checks, and metrics collection.
- `INCIDENT_RESPONSE.md`: On-call escalation and post-mortem procedures.
- `SECURITY_OPERATIONS.md`: Hardening audits, vulnerability remediation.

### Backup & Recovery Guides (`docs/backup-recovery/`)
- `BACKUP_POLICY.md`: RPO/RTO targets, schedules, and retention tiers.
- `DATABASE_BACKUP.md`: Automated pg_dump execution and off-host upload.
- `MEDIA_BACKUP.md`: Object storage and filesystem media snapshots.
- `RESTORE_PROCEDURE.md`: Point-in-time database restoration runbook.
- `DISASTER_RECOVERY.md`: Total data center / host recovery protocol.
- `RECOVERY_TEST_REPORT.md`: Semi-annual disaster drill verification report.

### Emergency Runbooks (`docs/runbooks/`)
- `API_UNAVAILABLE.md`: Triage and remediation for 502/503/504 errors.
- `DATABASE_UNAVAILABLE.md`: Connection pool exhaustion and database down.
- `WORKER_BACKLOG.md`: Resolving outbox queue congestion and dead letters.
- `STORAGE_UNAVAILABLE.md`: Handling S3 or local disk I/O failures.
- `CACHE_FAILURE.md`: Redis outage and graceful degradation verification.
- `FAILED_DEPLOYMENT.md`: Fast rollback procedure for bad releases.
- `FAILED_MIGRATION.md`: Reverting schema migration anomalies safely.
- `CERTIFICATE_EXPIRY.md`: Emergency SSL certificate renewal.
- `TENANT_DATA_INCIDENT.md`: Handling suspected cross-tenant data leakage.\n