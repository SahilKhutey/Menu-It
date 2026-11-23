# Storage Operations Guide
**ModularMenu Operational Documentation**

## 1. Local Storage Management (Customer-Hosted)
Local media assets reside at `/var/lib/modularmenu/media`.
```bash
# Check disk usage
du -sh /var/lib/modularmenu/media

# Clean up orphaned temporary uploads (> 24 hours old)
find /var/lib/modularmenu/media/tmp -type f -mtime +1 -delete
```

## 2. S3 / MinIO Storage Management (SaaS)
- Tenant media partitioned under `s3://modularmenu-media/tenants/{org_id}/`.
- Verify S3 connectivity:
```bash
bash infrastructure/scripts/verify-storage.sh
```\n