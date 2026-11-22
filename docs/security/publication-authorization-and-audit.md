# Publication Authorization & Audit Architecture (ARC-10 §15)

## Roles & Permissions
- `RestaurantOwner`: Full validation, publish, rollback, and scheduling permissions.
- `RestaurantManager`: Validation, routine publishing, and rollback.
- `MenuEditor`: Draft saving and validation only; publishing restricted.
- `Viewer`: Read-only draft view.

## Audit Logs
All publish, rollback, and schedule mutations record actor ID, client IP, target publication ID, and timestamp.
