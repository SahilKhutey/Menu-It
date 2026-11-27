# FCD-03 — Transaction Management & Atomic Boundaries

## 1. Principles of Transaction Boundaries

Multi-step business workflows must execute atomically. If an operation consists of creating a `Tenant` and an initial `Restaurant`, either both records must be committed together, or neither must exist in the database (automatic rollback).

### Rules of Transaction Management
1. **Service Ownership:** Transaction boundaries are owned by **Application Services** (`services/*`), not by repositories or endpoints.
2. **Context-Managed Transactions:** Use `async with session.begin():` to guarantee automatic commit on block exit and automatic rollback upon any unhandled exception.
3. **No Nested Independent Transactions:** Sub-operations participate in the existing transaction rather than starting competing independent transactions without savepoints.

---

## 2. Implementation: `TenantService`

Located at `apps/api/src/menu_it/services/tenant_service.py`:

```python
class TenantService:

  def __init__(self, session: AsyncSession):
    self.session = session
    self.tenants = TenantRepository(session)
    self.restaurants = RestaurantRepository(session)

  async def create_tenant_with_restaurant(
      self,
      *,
      tenant_name: str,
      tenant_slug: str,
      restaurant_name: str,
      restaurant_slug: str,
      timezone: str = "UTC",
  ) -> tuple[Tenant, Restaurant]:
    try:
      async with self.session.begin():
        # Preliminary uniqueness check
        if await self.tenants.slug_exists(tenant_slug):
          raise ResourceConflictError(
              f"Tenant slug '{tenant_slug}' is already registered."
          )

        tenant = Tenant(name=tenant_name, slug=tenant_slug)
        await self.tenants.create(tenant)

        restaurant = Restaurant(
            tenant_id=tenant.id,
            name=restaurant_name,
            slug=restaurant_slug,
            timezone=timezone,
        )
        await self.restaurants.create(restaurant)

        return tenant, restaurant
    except IntegrityError as exc:
      # Transaction has automatically rolled back
      raise ResourceConflictError(
          "A database uniqueness or integrity constraint was violated during"
          " tenant creation."
      ) from exc
```

---

## 3. Concurrency, Race Conditions & Rollback

A pre-check like `slug_exists()` is helpful for friendly messages, but cannot prevent concurrent race conditions when two requests check simultaneously.

The authoritative enforcement is the database constraint. When concurrent conflicts occur:
1. PostgreSQL raises an `IntegrityError`.
2. `session.begin()` aborts and executes a `ROLLBACK`.
3. The service catches `IntegrityError` and raises a clean `ResourceConflictError`.
4. The centralized exception handler returns HTTP 409 Conflict with sanitized RFC 7807/9457 JSON details.
