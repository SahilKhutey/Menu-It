# FCD-06 §13 — TypeScript Shared Contracts

## 1. Monorepo Shared Types Package

Located in `packages/shared-types/`:
- `packages/shared-types/src/common.ts`: UUID, ISO8601String, MoneyDTO, AddressDTO, RequestMetadata, APIError, APIResponse<T>, PaginationMeta, PaginatedResponse<T>.
- `packages/shared-types/src/organization.ts`: OrganizationLifecycleStatus, OrganizationReferenceDTO.
- `packages/shared-types/src/restaurant.ts`: RestaurantLifecycleStatus, OperatingHoursIntervalDTO, DailyOperatingHoursDTO, WeeklyOperatingScheduleDTO, RestaurantProfileResponse, RestaurantProfileUpdateRequest.
- `packages/shared-types/src/index.ts`: Module barrel export.

## 2. Synchronization Guarantee

All TypeScript types strictly mirror the Python Pydantic transport contracts defined in `apps/api/src/menu_it/contracts/`:

| Backend Pydantic Schema | Frontend TypeScript Interface |
| :--- | :--- |
| `APIResponse[T]` | `APIResponse<T>` |
| `ResponseMetadata` | `RequestMetadata` |
| `APIError` | `APIError` |
| `PaginationMeta` | `PaginationMeta` |
| `RestaurantProfileResponse` | `RestaurantProfileResponse` |
| `DailyOperatingHoursDTO` | `DailyOperatingHoursDTO` |
| `TimeRangeDTO` | `OperatingHoursIntervalDTO` |

Verified via `pnpm --filter @menu-it/shared-types typecheck` and `pnpm -r --if-present typecheck`.
