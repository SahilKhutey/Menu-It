# 06 — Reverse Proxy & TLS Architecture
**ARC-11: Infrastructure & Deployment Architecture**

## 1. Nginx Reverse Proxy Role
The reverse proxy acts as the single ingress gateway (`infrastructure/proxy/nginx.conf`), providing:
- TLS 1.2 and TLS 1.3 termination with modern cipher suites.
- Request routing:
  - `/api/` -> Backend API (`http://backend:8000/`)
  - `/health` -> Backend Health Probes (`http://backend:8000/health`)
  - `/docs`, `/openapi.json` -> Backend OpenAPI specs
  - `/media/` -> Local media storage (Customer-Hosted profile)
  - `/` -> Frontend Next.js Server (`http://frontend:3000/`)
- Rate limiting:
  - API zone: 100 requests/minute per client IP.
  - Media zone: 300 requests/minute per client IP.
- Security Headers:
  - `X-Content-Type-Options: nosniff`
  - `X-Frame-Options: SAMEORIGIN`
  - `X-XSS-Protection: 1; mode=block`
  - `Referrer-Policy: strict-origin-when-cross-origin`
  - `Content-Security-Policy: default-src 'self'; ...`\n