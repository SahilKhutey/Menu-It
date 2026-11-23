# Menu-It — Local Infrastructure & Docker Guide

**Document ID:** FCD01-DOC-08  
**Phase:** FCD-01 Development Environment & Repository Foundation  
**Audience:** All Software Engineers & DevOps Engineers  

---

## 1. Overview

Local development infrastructure for Menu-It is containerized via Docker Compose. The foundational local stack provisions a hardened **PostgreSQL 16** database container with health checks and persistent volume storage.

---

## 2. Architecture & Service Definition

The canonical local development Compose file is located at `infrastructure/development/docker-compose.yml` (and mirrored at root `compose.yaml`):

```yaml
services:
  postgres:
    image: postgres:16-alpine
    container_name: menu-it-postgres
    restart: unless-stopped
    environment:
      POSTGRES_DB: ${POSTGRES_DB:-menu_it_dev}
      POSTGRES_USER: ${POSTGRES_USER:-menu_it}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:?Set POSTGRES_PASSWORD}
    ports:
      - "127.0.0.1:5432:5432"
    volumes:
      - menu_it_postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U $${POSTGRES_USER} -d $${POSTGRES_DB}"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  menu_it_postgres_data:
```

### Security & Isolation Characteristics
1. **Loopback Port Binding:** Bound exclusively to `127.0.0.1:5432`, preventing exposure on external local networks.
2. **Persistent Named Volume:** `menu_it_postgres_data` preserves database state across container restarts and updates.
3. **Automated Health Probes:** Uses `pg_isready` to signal readiness before application containers connect.

---

## 3. Operational Commands

### Start Services
```powershell
docker compose -f infrastructure/development/docker-compose.yml --env-file .env up -d
```

### Verify Health & Status
```powershell
docker compose -f infrastructure/development/docker-compose.yml ps
```

### Execute Manual Health Check
```powershell
docker compose -f infrastructure/development/docker-compose.yml exec postgres pg_isready -U menu_it -d menu_it_dev
```

### Clean Shutdown
```powershell
# Stops containers, preserves volume data
docker compose -f infrastructure/development/docker-compose.yml down
```

### Complete Disposable Reset
```powershell
# WARNING: Deletes all local database data
docker compose -f infrastructure/development/docker-compose.yml down -v
```
