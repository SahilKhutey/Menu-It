# FCD-06 §05 — Organization Domain Contracts

## 1. Domain Concept

The Organization is the root multi-tenant boundary for Menu-It. While physical organization lifecycle operations are coordinated by FCD-04, FCD-06 provides the pure domain contracts for organization identity and referencing.

## 2. Organization Reference Contract

Located in `apps/api/src/menu_it/domain/organization/references.py`:

```python
@dataclass(frozen=True, slots=True)
class OrganizationReference:
    """Lightweight domain reference to a tenant organization."""
    organization_id: UUID
    display_name: str | None = None
```

## 3. Invariants & Rules

1. **Tenant Uniqueness**: Every business aggregate (RestaurantProfile, Menu, Order, etc.) must carry an explicit `organization_id`.
2. **Context Integrity**: The domain never relies on client-provided tenant headers. All operations must match the server-resolved `organization_id`.
3. **Cross-Tenant Prohibition**: Two entities with different `organization_id` values cannot interact directly or form relational associations.
