# 17 — Security & Hardening Architecture
**ARC-11: Infrastructure & Deployment Architecture**

## 1. Container Hardening Checklist
- [x] Non-root user execution (`UID 10001` menuapp, `UID 1000` node).
- [x] Read-only root container filesystems (`read_only: true`).
- [x] Ephemeral writable directories mounted via `tmpfs` (`/tmp:size=128m`).
- [x] Dropped all Linux capabilities (`cap_drop: [ALL]`).
- [x] Disabled privilege escalation (`no-new-privileges: true`).
- [x] Minimal scratch/distroless base images (`python:3.12-slim-bookworm`, `node:20-alpine`).
- [x] Automated CVE vulnerability scanning in CI/CD pipeline.\n