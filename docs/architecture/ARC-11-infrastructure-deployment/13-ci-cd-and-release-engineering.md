# 13 — CI/CD & Release Engineering
**ARC-11: Infrastructure & Deployment Architecture**

## 1. GitHub Actions Pipeline Structure
- `quality-gates.yml`: Executes on all pull requests and pushes to `main` and `develop`:
  - Gate 1: Ruff linter & formatting check (`ruff check backend/`, `ruff format --check backend/`).
  - Gate 2: Architecture test boundaries (`pytest tests/architecture/`).
  - Gate 3: Full platform automated test suite (738 tests passing 100%).
  - Gate 4: Frontend type checking, linting, and standalone build verification.
- `release.yml`: Triggered on git version tags (`v*`):
  - Builds multi-stage Docker images for frontend, backend, and worker.
  - Generates Software Bill of Materials (SBOM) in SPDX format.
  - Scans images for CVEs using Trivy.
  - Publishes tagged images with immutable digests to GitHub Container Registry (GHCR).\n