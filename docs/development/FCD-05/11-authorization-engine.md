# FCD-05 — Authorization Engine & Policy Evaluator

## 1. Authorization Architecture

The authorization engine in Menu-It operates as a zero-trust policy evaluation layer. It is implemented across:
- [policies.py](file:///c:/Users/ASUS/Documents/Menu-it/apps/api/src/menu_it/authorization/policies.py): Static mapping tables defining role capabilities.
- [evaluator.py](file:///c:/Users/ASUS/Documents/Menu-it/apps/api/src/menu_it/authorization/evaluator.py): Pure evaluation functions (`has_organization_permission`, `require_organization_permission`, etc.).
- [dependencies.py](file:///c:/Users/ASUS/Documents/Menu-it/apps/api/src/menu_it/authorization/dependencies.py): FastAPI dependency factories (`require_permission`, `require_platform_role`).

```mermaid
flowchart TD
    REQ["Incoming HTTP Request"] --> AUTH["Auth Middleware / Dependency\n(Bearer JWT + Session Validation)"]
    AUTH --> TENANT["TenantResolver\n(Resolves trusted TenantContext)"]
    TENANT --> PERM_CHECK{"require_permission(P)"}

    subgraph Evaluation["Permission Evaluation Engine"]
        PERM_CHECK --> ORG_EVAL["Evaluate Organization Role\nORGANIZATION_ROLE_PERMISSIONS[role]"]
        ORG_EVAL -- "Permission in set" --> ALLOW["Return TenantContext\n(Execute Endpoint)"]
        ORG_EVAL -- "Not in set" --> REST_CHECK{"Is restaurant_id set\n& restaurant_role set?"}
        REST_CHECK -- "Yes" --> REST_EVAL["Evaluate Restaurant Role\nRESTAURANT_ROLE_PERMISSIONS[role]"]
        REST_EVAL -- "Permission in set" --> ALLOW
        REST_EVAL -- "Not in set" --> DENY["403 Forbidden\n(PermissionDeniedError)"]
        REST_CHECK -- "No" --> DENY
    end
```

---

## 2. Declarative Route Protection

Endpoints declare permission requirements cleanly via dependency injection:
```python
@router.delete(
    "/{organization_id}/restaurants/{restaurant_id}",
    dependencies=[Depends(require_permission(Permission.RESTAURANT_ARCHIVE))],
)
async def archive_restaurant(...) -> ...:
    ...
```
This guarantees that developers cannot accidentally forget authorization checks, and every request is validated against the active server-resolved membership before the endpoint function is invoked.
