# FCD-07 §07 — Authentication & Dependency Injection Facade

## 1. Unified Dependencies Subsystem

The `apps/api/src/menu_it/api/dependencies/` package exposes a clean dependency injection facade for FastAPI route handlers:

```
menu_it.api.dependencies/
├── authentication.py      # AuthenticatedPrincipal resolution & JWT validation
├── tenant.py              # Server-side TenantContext resolution & RLS
├── permissions.py         # Declarative RBAC / permission guards
├── pagination.py          # Pagination parameter extraction & clamping
└── request_context.py     # Request ID and client IP extraction
```

---

## 2. Declarative Permission Guards

Route handlers enforce least-privilege access using declarative dependencies:

```python
@router.post(
    "",
    dependencies=[
        Depends(require_permission("restaurant:create")),
    ],
)
async def create_restaurant(...):
    ...
```

The `require_permission` dependency resolves permissions via `TenantContext.has_permission()` backed by the user's active membership role in the target organization. If the caller lacks the permission, a `403 Forbidden` response is returned immediately with `PERMISSION_DENIED`.

---

## 3. Platform Administration Boundary

Platform-level operations (such as system management and global analytics) use `require_platform_role`:
- Requires active platform membership in `platform_memberships`.
- Refuses regular tenant users regardless of organization permissions.
- Prevents horizontal privilege escalation.
