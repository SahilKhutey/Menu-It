# Contributing to Menu-It

Welcome to **Menu-It**! We welcome contributions to our modular, multi-tenant restaurant SaaS platform.

---

## 1. Development Process

1. **Start from `develop`:** Ensure your local branch is synchronized with the latest `develop` branch.
2. **Create a focused branch:** Name your branch following our conventions:
   - `feature/<name>` for new capabilities
   - `fix/<name>` for defect corrections
   - `hotfix/<name>` for urgent production fixes
3. **Implement your change:** Keep modifications modular, isolated, and aligned with architectural boundaries.
4. **Add relevant tests:** Every meaningful code change must include corresponding unit, integration, or contract tests.
5. **Update documentation:** Maintain relevant ADRs, architectural specs, and devlogs.
6. **Execute local checks:** Run formatting, linting, type checks, and tests before pushing.
7. **Submit a pull request:** Fill out the PR template with clear verification results and architectural context.

---

## 2. Commit Format

All commits must adhere to the **Conventional Commits** specification:

```
<type>(<scope>): <description>
```

Examples:
- `feat(auth): add Argon2id session hashing`
- `fix(tenant): prevent cross-tenant parameter leakage`
- `docs(fcd-01): update repository setup guide`
- `ci(quality-gates): add type checking stage`

---

## 3. Code Quality Invariants

- Follow language-specific standards (Ruff for Python, ESLint/Prettier for TypeScript).
- Never duplicate business logic across modules or workspaces.
- Never commit secrets, credentials, or live database dumps.
- Strictly maintain multi-tenant isolation and row-level security invariants.
- Test all meaningful changes with automated suites.

---

## 4. Pull Request Requirements

Every PR must explain:
- The purpose and motivation of the change.
- The files and modules affected.
- Architectural and security implications.
- Verification and test results.
