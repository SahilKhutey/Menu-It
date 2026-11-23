# Release Checklist & Quality Gates
**ModularMenu Operational Documentation**

## Pre-Release Verification
- [ ] Codebase on `develop` branch passes all 738 platform automated tests.
- [ ] Backend Ruff check (`ruff check backend/`) reports 0 errors.
- [ ] Backend Ruff formatting (`ruff format --check backend/`) reports 0 differences.
- [ ] Next.js frontend standalone bundle built and JS payload verified < 120 kB gzip.
- [ ] Architecture decisions registered in `docs/decisions/decision-register.md`.
- [ ] Devlog and Tasklog updated with complete release notes.

## Release Execution
- [ ] Merge `develop` into `main` with `--no-ff`.
- [ ] Create signed git release tag (e.g., `v1.0.0-arc11`).
- [ ] Push `main`, `develop`, and git tag to GitHub.
- [ ] Confirm GitHub Actions container image build and GHCR publication.\n