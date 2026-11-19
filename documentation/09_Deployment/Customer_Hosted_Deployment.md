# Customer-Hosted Deployment Architecture & Guide
**Document ID:** DEP-SELFHOST-001  
**Target:** Standalone Enterprise & On-Premise Installations

---

## 1. Customer-Hosted Edition Overview
ModularMenu provides a dedicated, customer-hosted Docker profile allowing restaurants and hospitality enterprises to run the platform on their own infrastructure (AWS EC2, DigitalOcean, Hetzner, Bare Metal, or private cloud) while maintaining the same underlying code framework as the Managed SaaS edition.

### Architecture Layout
```
Customer Host / VPS
  ├── Nginx / Reverse Proxy (Ports 80/443, SSL via Let's Encrypt)
  ├── Docker Compose Cluster
  │     ├── frontend (Next.js Standalone Container - Port 3000)
  │     ├── backend (FastAPI Python 3.12 Container - Port 8000)
  │     ├── postgres (PostgreSQL 16 Alpine Container - Port 5432)
  │     └── local_storage (/var/data/uploads mounted volume)
  └── Daily Backup Cron (Automated pg_dump + media tarball)
```

---

## 2. Directory Structure of Deployment Package
```
deployment/
├── docker-compose.yml
├── .env.example
├── nginx.conf
├── scripts/
│   ├── install.sh
│   ├── backup.sh
│   ├── restore.sh
│   └── healthcheck.sh
└── README.md
```

---

## 3. Deployment Configuration (`.env`)
```ini
DEPLOYMENT_MODE=self_hosted
ENVIRONMENT=production
PUBLIC_BASE_URL=https://menu.customerrestaurant.com
SECRET_KEY=change_this_to_a_random_64_character_hex_string

# PostgreSQL Credentials
POSTGRES_USER=modularmenu
POSTGRES_PASSWORD=secure_generated_database_password
POSTGRES_DB=modularmenu_db
DATABASE_URL=postgresql+asyncpg://modularmenu:secure_generated_database_password@postgres:5432/modularmenu_db

# Storage Provider (Local filesystem for self-hosted)
STORAGE_PROVIDER=local
STORAGE_LOCAL_PATH=/app/uploads

# Offline-Tolerant License Key
LICENSE_KEY=MMLIC-PRO-2026-CUSTOMER-001-A9F8E
LICENSE_GRACE_PERIOD_DAYS=30
```
