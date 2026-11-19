# ModularMenu (v1.0.0)
> Configurable, Multi-Tenant Digital Restaurant Menu Platform

---

## 🍽️ Overview

**ModularMenu** is a multi-tenant digital restaurant menu platform with a hybrid business model (Managed SaaS + Customer-Hosted Docker Profile), built India-First and Web-First.

- **Centralized Restaurant Management:** Multi-branch ready tenant hierarchy (`Organization -> Restaurant -> Menus`).
- **3-Panel Visual Studio:** Catalog tree, live mobile/tablet/desktop viewport preview, and theme inspector.
- **Dynamic Theme & Layout Engine:** 6 pre-built visual presets (*Luxury, Minimal, Rustic, Vibrant, Contemporary, Editorial*) with token-based CSS variables.
- **Immutable Snapshot Publishing:** Instant compile with SHA-256 checksums, atomic activation, and zero-downtime rollback.
- **Zero-Friction Public QR Experience:** Instant sub-second LCP on 360px+ mobile screens, FSSAI dietary badges, and allergen advisories.
- **Hardened Multi-Tenancy:** PostgreSQL Row-Level Security (RLS) + tenant-scoped authorization dependencies.

---

## 🏛️ Architecture & Tech Stack

| Layer | Technology |
| :--- | :--- |
| **Frontend Applications** | Next.js 14+ (App Router), React 18, TypeScript, Tailwind CSS, Lucide Icons |
| **Backend API** | FastAPI (Python 3.12), Pydantic v2, SQLAlchemy 2.0 Async |
| **Database & Migrations** | PostgreSQL 16 (Multi-tenant shared schema with RLS) + Alembic |
| **Security & Auth** | Argon2id / Bcrypt password hashing, HS256/RS256 JWT, Tenant Context Dependency |
| **Deployment Profiles** | Profile A: Managed Multi-Tenant SaaS · Profile B: Customer-Hosted Docker Profile |

---

## 🚀 Quickstart & Local Development

### 1. Backend Setup (FastAPI)
```bash
cd backend
python -m venv .venv
# On Windows:
.\.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
pytest -v
uvicorn app.main:app --reload --port 8000
```
- API Docs: `http://localhost:8000/docs`
- Health: `http://localhost:8000/health`

### 2. Frontend Setup (Next.js)
```bash
cd frontend
pnpm install
pnpm run build
pnpm run dev
```
- Homepage & Portals: `http://localhost:3000`
- Platform Admin: `http://localhost:3000/platform`
- Restaurant Visual Studio: `http://localhost:3000/app`
- Customer QR Experience: `http://localhost:3000/r/the-bombay-canteen`

### 3. Docker Compose (Full Stack)
```bash
docker compose up -d
```

---

## 📂 Project Documentation Framework

Comprehensive engineering blueprints and specifications are maintained in `documentation/`:
- `01_Product_Strategy/`: Vision, Business Model, Pricing Strategy
- `02_Product_Requirements/`: PRD, Functional & Non-Functional Requirements
- `03_System_Architecture/`: High-Level Diagrams, Domain Boundaries, Request Lifecycles
- `04_Module_Specifications/`: Specifications for MOD-01 to MOD-16
- `05_UI_UX_Design/`: Design Tokens, Theme Systems, 6 Visual Presets
- `06_Security/`: Tenant Isolation Test Matrix, RLS Policies, Threat Model
- `07_Implementation/`: 12 Work Packages (WP-01 to WP-12) & Milestones
- `09_Deployment/`: Managed Cloud vs. Customer-Hosted Architecture Guide
