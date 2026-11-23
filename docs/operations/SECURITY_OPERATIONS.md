# Security Operations Guide
**ModularMenu Operational Documentation**

## 1. Hardening & Compliance Audits
- Verify non-root container users:
```bash
docker inspect --format='{{.Config.User}}' menu-backend  # Returns 10001
```
- Verify read-only root filesystems:
```bash
docker inspect --format='{{.HostConfig.ReadonlyRootfs}}' menu-backend  # Returns true
```

## 2. Secret Rotation Routine
Rotate `JWT_SECRET` and `SECRET_KEY` semi-annually with overlapping grace periods.\n