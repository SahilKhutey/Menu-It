# Menu-It — Git Workflow & Branching Strategy

**Document ID:** FCD01-DOC-06  
**Phase:** FCD-01 Development Environment & Repository Foundation  
**Audience:** All Software Engineers & Contributors  

---

## 1. Branching Strategy

Menu-It follows a modified GitFlow branching model centered on two perpetual branches:

```
main (Production Releases)
 │
 └── develop (Active Development Integration)
      │
      ├── feature/fcd-01-repository-foundation
      ├── feature/fcd-02-application-bootstrap
      ├── fix/database-connection-leak
      └── hotfix/critical-security-patch
```

### Branch Responsibilities
- **`main`:** Contains production-tested, stable releases. Code is merged here strictly from `develop` via audited pull requests or tagged release commits.
- **`develop`:** Primary integration branch. All feature branches and non-emergency bugfixes merge into `develop`.
- **`feature/*`:** Short-lived branches dedicated to a specific work package or architectural milestone.
- **`fix/*`:** Dedicated branches resolving bugs discovered during testing or review.
- **`hotfix/*`:** Urgent security or operational patches applied directly to `main` and backported to `develop`.

---

## 2. Conventional Commit Standards

All commits must follow the **Conventional Commits** specification:

```
<type>(<scope>): <short imperative description>

[optional body explaining motivation and architectural impact]

[optional footer referencing issue or breaking change]
```

### Allowed Types
- **`feat`:** A new user-facing or platform capability.
- **`fix`:** A bug fix or defect correction.
- **`docs`:** Documentation changes only.
- **`refactor`:** Code restructuring without altering external behavior.
- **`test`:** Adding or correcting automated tests.
- **`build`:** Changes impacting build systems, dependencies, or tooling.
- **`ci`:** Continuous integration workflow and automation changes.
- **`chore`:** Maintenance tasks, dependency updates, or housekeeping.

### Examples
- `feat(auth): implement Argon2id password hashing and session rotation`
- `fix(tenant): prevent cross-tenant parameter leakage in menu query`
- `docs(fcd-01): publish repository foundation and environment setup guide`
- `ci(quality-gates): add type checking and ruff format checks`

---

## 3. Pull Request Standards

Every pull request must:
1. Reference the relevant Work Package (e.g., `FCD-01 / WP-02`).
2. Include an updated implementation checklist.
3. Confirm that all local tests and lint checks pass.
4. Document any configuration or database migration requirements.
5. Provide UI screenshots or terminal evidence for significant changes.
