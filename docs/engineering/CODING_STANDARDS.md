# Menu-It — Engineering & Coding Standards

**Document ID:** FCD01-DOC-04  
**Phase:** FCD-01 Development Environment & Repository Foundation  
**Audience:** All Software Engineers & Code Reviewers  

---

## 1. Core Engineering Principles

Every contribution to Menu-It must adhere to our fundamental principles:

1. **Single Responsibility Principle (SRP):** Each class, module, and component must have one, and only one, reason to change.
2. **Explicit Dependency Boundaries:** High-level domain logic must never depend directly on low-level infrastructure details; depend on abstractions and protocols.
3. **Zero Secrets in Code:** Passwords, API keys, JWT secrets, and tokens must never appear in source code or default configuration files.
4. **Type-Safe Interfaces:** Strict type hints in Python (`typing`, `pydantic`) and strict type checks in TypeScript (`strict: true`, no `any`).
5. **No Duplicate Business Logic:** Shared algorithms, calculations, and validations must reside in canonical packages or domain services.
6. **Immutable Snapshots for Read Paths:** Public diner menu data is served from immutable pre-compiled snapshots; never run complex ad-hoc joins on hot diner requests.
7. **Monetary Precision:** Always use integer cents/paise or `Decimal` for currency amounts. Never use floating-point types (`float` / `double`).
8. **Timezone Awareness:** All timestamps must be stored and manipulated in UTC. Local time formatting occurs exclusively at the presentation edge.

---

## 2. Naming Conventions

| Language / Domain | Construct | Convention | Example |
| :--- | :--- | :--- | :--- |
| **TypeScript / React** | Component Name | `PascalCase` | `MenuCard`, `ThemeProvider` |
| **TypeScript** | Variable / Function | `camelCase` | `activeTenantId`, `fetchMenuSnapshot()` |
| **TypeScript** | Interface / Type | `PascalCase` | `RestaurantDto`, `MenuItemContract` |
| **TypeScript** | Constant | `UPPER_SNAKE_CASE` | `MAX_UPLOAD_SIZE_BYTES` |
| **Python** | Module / File Name | `snake_case` | `tenant_service.py`, `menu_repository.py` |
| **Python** | Class Name | `PascalCase` | `TenantService`, `AuditLogger` |
| **Python** | Function / Method | `snake_case` | `get_published_menu()`, `rotate_session()` |
| **Python** | Constant / Global | `UPPER_SNAKE_CASE` | `DEFAULT_CACHE_TTL_SECONDS` |
| **Database** | Table Name | `snake_case` (plural) | `restaurants`, `menu_items`, `audit_logs` |
| **Database** | Column Name | `snake_case` | `organization_id`, `created_at` |
| **Git** | Branch Name | `kebab-case` | `feature/fcd-01-foundation`, `fix/login-csrf` |

---

## 3. Python Engineering Standards

### 3.1 Tooling & Configuration
- **Runtime:** Python 3.12+ (strictly pinned to Python 3.12 runtime).
- **Linter & Formatter:** **Ruff** (line length 100 characters).
- **Type Checker:** Pyright / Pylance (`typeCheckingMode = "strict"`).
- **Test Framework:** `pytest` with `pytest-asyncio`.

### 3.2 Code Quality Rules
- Explicit typing on all public functions, return types, and dataclasses/models.
- Never use bare `except:` clauses; always catch explicit exception types.
- Follow RFC 7807 / RFC 9457 structured error format for all API exceptions.
- Prefer Python 3.12 union syntax (`X | None`) over `Optional[X]`.

---

## 4. TypeScript & Frontend Standards

### 4.1 Tooling & Configuration
- **Runtime:** Node.js 20+ / 24 LTS.
- **Package Manager:** `pnpm`.
- **Framework:** Next.js 14 App Router.
- **Linter & Formatter:** ESLint + Prettier.
- **Styling:** Tailwind CSS with centralized design tokens.

### 4.2 Quality Constraints
- Enable `strict: true` in `tsconfig.json`.
- Disallow `any`; use `unknown` with runtime type narrowing or defined interfaces.
- Client components (`'use client'`) must be kept at the leaf nodes of the component tree to maximize server component performance.
- All diner-facing web pages must adhere to the 120 kB gzipped initial JS bundle budget.

---

## 5. Code Review Quality Gates

Every pull request must pass the following criteria before merge:
- [ ] 100% green CI pipeline (lint, format, typecheck, tests, build).
- [ ] Meaningful test coverage added or updated for new business logic.
- [ ] Zero committed secrets, environment variables, or local `.env` files.
- [ ] Conventional Commit format applied to all commit messages.
- [ ] Architectural invariants and tenant boundary constraints respected.
