# FCD-12 · Document 10: Artifact & Container Strategy

**Phase:** FCD-12 — Automated Testing & CI/CD Foundation  
**System:** Menu-It Restaurant SaaS Platform  
**Status:** Completed & Approved  
**Date:** 2026-11-26  

---

## 1. Container Images & Build Targets

Menu-It defines three containerization targets:

| Image | Dockerfile | Base Image | Runtime Port |
| :--- | :--- | :--- | :--- |
| **`menu-it-api`** | `apps/api/Dockerfile` | `python:3.12-slim` | 8000 |
| **`menu-it-web`** | `apps/web/Dockerfile` | `node:22-alpine` | 3000 |
| **`menu-it-admin`** | `apps/admin/Dockerfile` | `node:22-alpine` | 3001 |

---

## 2. Image Tagging & Digest Invariant

- Every build tags images with the short Git commit SHA: `menu-it-api:<git-sha>`.
- Release deployments use immutable SHA-256 container digests (`menu-it-api@sha256:...`) to ensure absolute reproducibility and prevent tag-mutation attacks.
- Non-root user (`appuser:1001`) enforced across all runtime containers.
