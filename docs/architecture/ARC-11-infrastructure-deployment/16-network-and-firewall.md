# 16 — Network & Firewall Architecture
**ARC-11: Infrastructure & Deployment Architecture**

## 1. Port Exposure Rules
- **Publicly Accessible:** Port 80 (HTTP redirect), Port 443 (HTTPS TLS termination) via Nginx.
- **Internal Only:**
  - Port 8000: FastAPI Backend (accessible only from `proxy` and `worker`).
  - Port 3000: Next.js Frontend (accessible only from `proxy`).
  - Port 5432: PostgreSQL Database (accessible only from `backend` and `worker`).
  - Port 6379: Redis Cache (accessible only from `backend` and `worker`).
- Ingress firewall blocks all external direct access to database and cache ports.\n