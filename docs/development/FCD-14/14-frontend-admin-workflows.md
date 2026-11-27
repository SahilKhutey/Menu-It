# FCD-14 — 14 Frontend Admin Workflows (`apps/admin`)

## Pages Implemented
- `/organizations` (`apps/admin/src/app/organizations/page.tsx`): Platform-level organization directory with status inspection and suspension controls.
- `/restaurants` (`apps/admin/src/app/restaurants/page.tsx`): Cross-organization restaurant oversight and lifecycle management.
- `/branches` (`apps/admin/src/app/branches/page.tsx`): Branch operational overview including independent branch timezones and lifecycle status.

## Design System Alignment
Both `apps/web` and `apps/admin` consume shared components from `@menu-it/ui` (FCD-08) and typed contracts from `@menu-it/shared-types`.
