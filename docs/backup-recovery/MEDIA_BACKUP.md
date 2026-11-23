# Media Storage Backup Procedure
**ModularMenu Operational Documentation**

## 1. Local Storage Backup (Customer-Hosted)
```bash
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
tar -czf "/var/backups/modularmenu/media_${TIMESTAMP}.tar.gz" -C /var/lib/modularmenu media
```

## 2. Cloud Storage Backup (SaaS)
S3 buckets configured with versioning and automatic replication to a secondary disaster recovery region.\n