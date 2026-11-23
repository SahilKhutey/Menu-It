# Menu-It — Development Toolchain & Runtime Specification

**Document ID:** FCD01-DOC-07  
**Phase:** FCD-01 Development Environment & Repository Foundation  
**Audience:** All Software Engineers & System Administrators  

---

## 1. Approved Runtime & Tooling Matrix

To guarantee build reproducibility across developer workstations, Docker containers, and GitHub Actions CI runners, the following runtimes and tools are pinned:

| Category | Component / Tool | Approved Version | Purpose |
| :--- | :--- | :--- | :--- |
| **Backend Runtime** | Python | `3.12.x` | Core backend execution engine |
| **Backend Framework** | FastAPI | `>=0.110.0, <1.0.0` | High-performance async REST API |
| **Database ORM** | SQLAlchemy | `>=2.0.28, <3.0.0` | Async relational persistence & Unit of Work |
| **Migrations** | Alembic | `>=1.13.1, <2.0.0` | Schema change management |
| **Frontend Runtime** | Node.js | `20 LTS / 24 LTS` | Frontend build and runtime environment |
| **Frontend Framework**| Next.js | `14.1.4` (App Router) | Customer-facing diner presentation |
| **Package Manager** | pnpm | `9.x / 11.x` | Deterministic monorepo dependency manager |
| **Python Tooling** | Ruff | `0.16.x` | Ultra-fast Python linter and formatter |
| **Python Typing** | Pyright / Pylance | Modern | Strict static type verification |
| **Database Engine** | PostgreSQL | `16.x` | Canonical multi-tenant transactional database |
| **Containers** | Docker Engine | Modern (24+) | Containerization & local service isolation |
| **Orchestration** | Docker Compose | `v2.x` | Local multi-service infrastructure composition |

---

## 2. Windows Development Considerations

For engineers developing on Windows:
- **Line Endings:** Git must be configured with `core.autocrlf = true` or managed via `.gitattributes` (`eol=lf` for source files, `eol=crlf` for PowerShell scripts).
- **Execution Policy:** When running local automation scripts, use `-ExecutionPolicy Bypass`:
  ```powershell
  powershell -ExecutionPolicy Bypass -File scripts/development/setup.ps1
  ```
- **Virtual Environments:** Python virtual environments on Windows are located in `backend/.venv/Scripts/python.exe`.
