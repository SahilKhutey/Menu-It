# Menu-It — Development Setup Guide

**Document ID:** FCD01-DOC-02  
**Phase:** FCD-01 Development Environment & Repository Foundation  
**Audience:** All Software Engineers & Contributors  

---

## 1. Quickstart

To set up the complete Menu-It development environment on a fresh workstation:

```powershell
# 1. Clone the repository
git clone https://github.com/SahilKhutey/Menu-It.git
Set-Location Menu-It

# 2. Configure local development environment
Copy-Item .env.example .env

# 3. Execute automated setup script
powershell -ExecutionPolicy Bypass -File scripts/development/setup.ps1
```

---

## 2. Prerequisites & Toolchain Verification

Ensure the following runtimes and tools are installed:

| Tool | Minimum Version | Purpose | Verification Command |
| :--- | :--- | :--- | :--- |
| **Git** | 2.40+ | Source version control | `git --version` |
| **Node.js** | 20+ / 24 LTS | Frontend runtime | `node --version` |
| **pnpm** | 9+ / 11+ | Frontend workspace manager | `pnpm --version` |
| **Python** | 3.12+ | Backend runtime | `python --version` |
| **Ruff** | 0.16+ | Python linter and formatter | `ruff --version` |
| **Docker Desktop** | Modern | Local services & containers | `docker --version` |

Run the automated environment verification preflight tool:
```powershell
powershell -ExecutionPolicy Bypass -File scripts/validation/verify-environment.ps1
```

---

## 3. Frontend Development Workflow

The frontend is built with **Next.js 14**, **TypeScript**, and **Tailwind CSS**.

From the `frontend/` directory (or root via pnpm):
```powershell
# Install frontend dependencies
pnpm install

# Start Next.js development server (http://localhost:3000)
pnpm run dev

# Run TypeScript type check
pnpm exec tsc --noEmit

# Run ESLint check
pnpm run lint

# Build production bundle
pnpm run build
```

---

## 4. Backend Development Workflow

The backend is built with **Python 3.12**, **FastAPI**, **SQLAlchemy 2.0 (asyncio)**, and **Alembic**.

From the `backend/` directory:
```powershell
# Activate Python virtual environment (Windows)
.\.venv\Scripts\Activate.ps1

# Install / verify dependencies
python -m pip install -r requirements.txt

# Run backend automated checks
powershell -ExecutionPolicy Bypass -File scripts/development/backend-check.ps1
```

Or run individual backend commands:
```powershell
# Lint check with Ruff
ruff check backend/

# Format check with Ruff
ruff format --check backend/

# Format in place
ruff format backend/

# Run pytest test suite
pytest tests/unit/ tests/contract/ tests/architecture/ -v
```

---

## 5. Local Infrastructure (PostgreSQL & Docker)

To run the local database infrastructure:
```powershell
# Start local PostgreSQL service
docker compose -f infrastructure/development/docker-compose.yml --env-file .env up -d

# Verify container health
docker compose -f infrastructure/development/docker-compose.yml ps

# Stop local infrastructure
docker compose -f infrastructure/development/docker-compose.yml down
```

---

## 6. Daily Engineering Checklist

Before creating a pull request:
1. Ensure your branch is branched from `develop`: `git checkout -b feature/your-feature-name`.
2. Format code: `ruff format backend/` and `pnpm run format`.
3. Verify type checking: `pnpm exec tsc --noEmit` and `pyright` (or `ruff check backend/`).
4. Execute tests: `pytest tests/`.
5. Write commit messages following Conventional Commits format (`feat(...)`, `fix(...)`, `docs(...)`).
