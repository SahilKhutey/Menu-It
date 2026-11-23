# 04 — Container Architecture
**ARC-11: Infrastructure & Deployment Architecture**

## 1. Container Packaging Strategy
ModularMenu packages all execution runtimes into standard OCI-compliant container images using multi-stage Dockerfiles.

### Frontend Container (`infrastructure/docker/frontend.Dockerfile`)
- **Base Image:** `node:20-alpine` (multi-stage build).
- **Stages:**
  1. `deps`: Installs production and build dependencies via `pnpm fetch` / `pnpm install --frozen-lockfile`.
  2. `builder`: Generates Next.js standalone server build (`output: "standalone"`).
  3. `runner`: Minimal Alpine runtime copying only `.next/standalone`, `.next/static`, and `public`.
- **User:** Runs as unprivileged `nextjs` user (`UID 1001, GID 1001`).
- **Healthcheck:** Queries `http://127.0.0.1:3000/api/health` every 30s.

### Backend Container (`infrastructure/docker/backend.Dockerfile`)
- **Base Image:** `python:3.12-slim-bookworm` (multi-stage build).
- **Stages:**
  1. `builder`: Compiles wheel dependencies in a virtual environment (`/opt/venv`).
  2. `runtime`: Copies virtual environment, creates user `menuapp` (`UID 10001, GID 10001`).
- **Security:** Root filesystem mounted read-only; `/tmp` provided as ephemeral tmpfs.
- **Healthcheck:** Queries `http://127.0.0.1:8000/health/live` every 15s.

### Worker Container (`infrastructure/docker/worker.Dockerfile`)
- **Base Image:** `python:3.12-slim-bookworm`.
- **Runtime:** Shares identical base and dependencies with backend, executing `app.worker` entrypoint.
- **User:** `menuapp` (`UID 10001, GID 10001`).
- **Lifecycle:** Handles `SIGTERM` and `SIGINT` signals with graceful shutdown of pending transactional outbox jobs.\n