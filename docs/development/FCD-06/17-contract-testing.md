# FCD-06 §17 — Contract Testing & Schema Verification

## 1. Objectives

Contract tests guarantee that:
1. API responses conform to the standard `{success, data, error, meta}` contract envelope.
2. Error responses include standard error codes and detail arrays.
3. Pagination schemas accurately calculate `total_pages`, `has_next`, and `has_previous`.
4. TypeScript definitions in `@menu-it/shared-types` are completely compatible with backend DTOs.

## 2. Test Execution

- Python Contract Tests:
  `python -m pytest apps/api/tests/contract -v`
  - 9 tests passing in 0.32s.
- TypeScript Verification:
  `pnpm --filter @menu-it/shared-types typecheck`
  - TypeScript `tsc --noEmit` exits with status 0.
- Monorepo Cross-Project Typecheck:
  `pnpm -r --if-present typecheck`
  - `packages/shared-types`, `apps/web`, and `apps/admin` all pass.
