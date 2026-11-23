# 05 — Compose Orchestration
**ARC-11: Infrastructure & Deployment Architecture**

## 1. Orchestration Philosophy
ModularMenu standardizes on Docker Compose v2 as the primary runtime orchestrator. This provides a balance of production reliability, infrastructure portability, and operational simplicity without introducing premature Kubernetes overhead.

## 2. Compose Configuration Files
- `compose.yaml`: Base service definitions (frontend, backend, worker, postgres, redis, proxy).
- `compose.dev.yaml`: Development overrides (volume mounts for hot reload, debug port mappings).
- `compose.production.yaml`: Hardened production SaaS stack (read-only rootfs, resource limits, internal networks).
- `compose.customer-hosted.yaml`: Self-contained appliance stack with local storage and volume definitions.

## 3. Network Isolation Topology
- `public-net`: External bridge connecting Nginx reverse proxy to public internet.
- `app-net`: Internal bridge connecting Nginx, Frontend, and Backend API.
- `data-net`: Strictly internal isolated bridge connecting Backend, Worker, PostgreSQL, and Redis. External traffic cannot reach `data-net`.\n