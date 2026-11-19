# Contributing to ModularMenu

Welcome to the **ModularMenu** engineering team. To preserve the system's modularity, multi-tenant isolation, and binary portability, all contributions must adhere to the engineering standards defined in **ARC-01** and **ARC-02**.

---

## 1. Branching & Commit Conventions

### 1.1 Branch Strategy
- `main`: Production-ready, stable releases. Direct commits are forbidden.
- `develop`: Integration branch for tested and reviewed features.
- `feature/<name>`: Feature branches cut from `develop`.
- `fix/<name>`: Bug fix branches cut from `develop`.
- `arch/<name>`: Architecture and governance documentation branches.

### 1.2 Conventional Commits
All commit messages must follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:
```
<type>(<scope>): <short description in imperative present tense>

[optional body explaining architectural context or rationale]

[optional footer referencing issue or ADR]
```

#### Allowed Types:
- `feat`: A new user-facing or platform capability.
- `fix`: A bug fix or patch.
- `docs`: Documentation updates (e.g. `docs(arch): update ARC-02 test matrix`).
- `style`: Formatting changes that do not affect code semantics.
- `refactor`: Code restructuring without functional changes.
- `perf`: Performance optimizations.
- `test`: Adding or updating test suites.
- `chore`: Build tooling, dependency, or CI/CD updates.

#### Scopes:
- `core`, `auth`, `tenant`, `menus`, `themes`, `publishing`, `renderer`, `infra`.

---

## 2. Architectural Rules & Non-Negotiables

1. **Zero Code Forks (Principle P-03):** Never fork or create client-specific branches to customize restaurant styling or features. All customization is driven by JSON configuration tokens.
2. **Tenant Isolation (Principle P-04):** Never write a database query or endpoint that omits tenant qualification (`restaurant_id`). Every tenant-scoped request must be authenticated and authorized.
3. **Monetary Precision (Constraint CON-05):** Always use fixed-precision `Numeric(12,2)` or integer minor units (paise/cents). Never use floating-point types (`float`) for prices or amounts.
4. **Immutable Snapshots (Principle P-07):** Public menus are served from pre-compiled, frozen snapshots. Never join relational tables on the public QR scan path.
5. **Dual-Model Compatibility (Principle P-08):** Features must run identically in both Managed SaaS and Customer-Hosted Docker environments without code alterations.

---

## 3. Local Development & Verification Workflow

### 3.1 Backend Setup & Quality Checks
```bash
cd backend
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt

# Run linting and formatting checks
ruff check .
ruff format --check .

# Run all test suites
pytest
```

### 3.2 Frontend Setup & Quality Checks
```bash
cd frontend
pnpm install

# Run linting and type checking
pnpm run lint
npx tsc --noEmit

# Verify production build
pnpm run build
```

---

## 4. Submitting a Pull Request

1. Ensure all local tests pass and linters report 0 errors.
2. Open a Pull Request against `develop`.
3. Complete every item in `.github/pull_request_template.md`.
4. Ensure all automated GitHub Actions quality gates pass.
5. Obtain approval from the designated `CODEOWNERS` before merging.
