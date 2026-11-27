# FCD-14 — 13 Frontend Web Workflows (`apps/web`)

## Pages Implemented
- `/onboarding/organization` (`apps/web/src/app/onboarding/organization/page.tsx`): Self-service organization creation wizard.
- `/dashboard/organizations` (`apps/web/src/app/dashboard/organizations/page.tsx`): Organization switcher & list.
- `/dashboard/organizations/[organizationId]` (`page.tsx`): Organization overview dashboard.
- `/dashboard/organizations/[organizationId]/settings` (`settings/page.tsx`): Organization profile & regional settings.
- `/dashboard/organizations/[organizationId]/members` (`members/page.tsx`): Member directory, role management, ownership transfer, and email invitations.
- `/dashboard/organizations/[organizationId]/restaurants` (`restaurants/page.tsx`, `restaurants/new/page.tsx`): Restaurant list and creation form.
- `/dashboard/organizations/[organizationId]/restaurants/[restaurantId]/branches` (`branches/page.tsx`, `branches/new/page.tsx`): Branch list, independent timezone display, and branch creation form.
