# FCD-06 §06 — Restaurant Domain Models & References

## 1. Domain Concept

A Restaurant represents an operational restaurant location or branch owned by an Organization. It defines the physical boundaries of customer interaction, dining, kitchen operations, and menu presentation.

## 2. Restaurant Reference Contract

Located in `apps/api/src/menu_it/domain/restaurant/references.py`:

```python
@dataclass(frozen=True, slots=True)
class RestaurantReference:
    """Lightweight domain reference to a restaurant and its owning organization."""
    restaurant_id: UUID
    organization_id: UUID
    display_name: str | None = None
```

## 3. Ownership Invariant Verification

Located in `apps/api/src/menu_it/domain/restaurant/ownership.py`:

```python
def assert_restaurant_belongs_to_organization(
    restaurant_org_id: UUID,
    context_org_id: UUID,
) -> None:
    if restaurant_org_id != context_org_id:
        raise BusinessRuleViolationError(
            f"Tenant ownership mismatch: restaurant belongs to organization '{restaurant_org_id}', "
            f"not authorized tenant '{context_org_id}'."
        )
```

This invariant enforces that a restaurant's owning organization identically matches the active request's authenticated tenant context.
