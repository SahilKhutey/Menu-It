# 08 — Backend Tenant Enforcement

## 1. Explicit Service Scope Passing

In accordance with Clean Architecture and ARC05-D07, `TenantContext` is explicitly passed as an argument to use cases:

```python
class CreateMenuUseCase:
    def execute(self, command: CreateMenuCommand, context: TenantContext) -> MenuEntity:
        # 1. Authorize role and branch
        self.auth_policy.require(context, Permission.MENU_CREATE, restaurant_id=command.restaurant_id)
        # 2. Persist with tenant scope
        return self.menu_repo.create(organization_id=context.organization_id, ...)
```

## 2. Scoped Repositories

`TenantScopedRepository` guarantees that:
- `get_by_id(context, id)` validates `entity.organization_id == context.organization_id`.
- Foreign entity queries return `None` (preventing ID enumeration).
- Direct writes verify entity ownership matching `context.organization_id`.
