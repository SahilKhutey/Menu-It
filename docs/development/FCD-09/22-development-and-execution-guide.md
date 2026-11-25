# FCD-09 §22 — Development & Execution Guide

## 1. Local Development Setup

### 1.1 Python API Setup
```bash
cd apps/api
# Run migrations
python -m alembic upgrade head

# Run tests
python -m pytest tests -v
```

### 1.2 Starting Services
```bash
# Start all processes (API, Web, Admin)
pnpm dev

# Or start API individually
pnpm dev:api
```

---

## 2. File Upload & Notification Usage

### Uploading a File via CLI
```bash
curl -X POST http://127.0.0.1:8000/api/v1/files \
  -H "Authorization: Bearer <TOKEN>" \
  -H "X-Organization-ID: <ORG_UUID>" \
  -F "file=@restaurant-logo.png" \
  -F "visibility=tenant_private"
```

### Retrieving In-App Notifications
```bash
curl http://127.0.0.1:8000/api/v1/notifications \
  -H "Authorization: Bearer <TOKEN>"
```
