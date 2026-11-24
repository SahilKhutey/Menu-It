# FCD-07 §12 — Internal Service Communication & Application Boundaries

## 1. Modular Monolith Communication Philosophy

Menu-It is organized as a modular monolith. To maintain high cohesion and loose coupling between domains (such as menus, orders, tables, and restaurant management):
1. Modules **must not** perform raw SQL joins across foreign module tables.
2. Modules communicate internally via defined Python protocols and services.
3. Operations return `ApplicationResult[T]` to avoid unchecked exception propagation across module boundaries.

---

## 2. Standard Application Result Container

`ApplicationResult[T]` provides an explicit, type-safe return wrapper for application service methods:

```python
from menu_it.services.results import ApplicationResult

result = await restaurant_query_svc.get_restaurant(org_id, restaurant_id)
if result.is_success:
    dto = result.value
else:
    logger.warning("Lookup failed: %s (%s)", result.error, result.error_code)
```

### Methods & Properties
- `is_success`: Boolean indicating whether operation completed successfully.
- `is_failure`: Complement of `is_success`.
- `value`: Returns inner value `T` or raises `ValueError` if failed.
- `error`: Explanatory failure message.
- `error_code`: Machine-readable error code.
- `unwrap()`: Unwraps `value` or raises.
- `unwrap_or(default)`: Returns inner value if successful, or fallback.

---

## 3. Cross-Module Query Protocol (`RestaurantQueryService`)

The `RestaurantQueryService` protocol in `apps/api/src/menu_it/services/interfaces.py` specifies the contract for querying restaurant details from other application domains:

```python
class RestaurantQueryService(Protocol):
    async def get_restaurant(
        self,
        organization_id: UUID,
        restaurant_id: UUID,
    ) -> ApplicationResult[RestaurantLookupDTO]: ...

    async def is_restaurant_active(
        self,
        organization_id: UUID,
        restaurant_id: UUID,
    ) -> ApplicationResult[bool]: ...
```

By coding against this protocol, future modules like orders or menus remain completely independent of the underlying SQLAlchemy repository implementation.
