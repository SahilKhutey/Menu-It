# Runbook: Storage Unavailable / Upload Failures
**ModularMenu Emergency Runbook**

## 1. Symptoms
- Media uploads fail with HTTP 500 or StorageException.
- Menu images fail to render.

## 2. Diagnostic Steps
```bash
# Local storage check
df -h /var/lib/modularmenu/media

# S3 check
bash infrastructure/scripts/verify-storage.sh
```

## 3. Remediation
- Free up disk space if local drive is full.
- Verify AWS IAM credentials and S3 bucket endpoint connectivity.\n