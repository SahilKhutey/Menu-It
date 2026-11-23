# 01 — Infrastructure Overview
**ARC-11: Infrastructure & Deployment Architecture**

## 1. Executive Summary
ModularMenu's infrastructure is engineered to deliver zero-configuration-drift deployments across two distinct deployment targets:
1. **Managed SaaS Edition (Multi-Tenant):** Centrally operated cloud platform with PostgreSQL Row-Level Security (RLS), distributed S3/MinIO object storage, and optional Redis caching/rate-limiting.
2. **Customer-Hosted Edition (Single-Tenant/Appliance):** Self-contained, single-server deployment optimized for on-premise restaurant hardware or private virtual servers, utilizing local disk storage with HMAC signed URLs and optional Redis.

Both deployment models run identical application code, domain entities, database schemas, and API contracts.

## 2. Infrastructure Topology
```
                          +-------------------------+
                          |   Nginx Reverse Proxy   |
                          |  Port 80/443 (TLS Term) |
                          +-------------------------+
                                       |
                   +-------------------+-------------------+
                   |                                       |
                   v                                       v
         +--------------------+                  +--------------------+
         |  Next.js Frontend  |                  |  FastAPI Backend   |
         |  (Port 3000, Node) |                  |  (Port 8000, Py312)|
         +--------------------+                  +--------------------+
                                                           |
                                      +--------------------+--------------------+
                                      |                                         |
                                      v                                         v
                            +--------------------+                    +--------------------+
                            | PostgreSQL 16 DB   |                    | Background Worker  |
                            | (Port 5432, RLS)   |                    | (Outbox & Jobs)    |
                            +--------------------+                    +--------------------+
                                      |                                         |
                                      +--------------------+--------------------+
                                                           |
                                                           v
                                                 +--------------------+
                                                 | Redis 7 (Optional) |
                                                 | (Port 6379, Cache) |
                                                 +--------------------+
```

## 3. Technology Stack Standardization
- **Host OS:** Linux (Ubuntu 22.04 LTS / Debian 12 Bookworm recommended) or Docker-compatible host.
- **Orchestration:** Docker Engine >= 24.0, Docker Compose >= 2.20.
- **Web Server / Reverse Proxy:** Nginx 1.25 Alpine with custom security configuration.
- **Backend Runtime:** Python 3.12 (Debian Bookworm slim).
- **Frontend Runtime:** Node.js 20 (Alpine slim), Next.js 14 Standalone.
- **Database:** PostgreSQL 16 with UUID and Row-Level Security enabled.
- **Cache / Ephemeral Store:** Redis 7.2 Alpine (strictly non-authoritative).
- **Object Storage:** AWS S3 / MinIO (SaaS) or Local File System with HMAC signing (Customer-Hosted).\n