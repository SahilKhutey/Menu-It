# FCD-03 — Repository Pattern & Data Access Layer

## 1. Principles & Architectural Role

Repositories isolate data persistence and querying logic from HTTP handling and business services.

### Core Repository Invariants
1. **Injected Session:** Repositories NEVER instantiate engines or sessions independently. The caller supplies the session.
2. **Never Commit:** Repositories NEVER call `session.commit()`. Calling `session.flush()` synchronizes SQL state while letting the outer application service maintain transaction boundaries.
3. **Pure Persistence:** Repositories do not parse HTTP status codes, authorize users, or handle routing.

---

## 2. Generic Base Repository (`BaseRepository[T]`)

Defined in `apps/api/src/menu_it/repositories/base.py`:

```python
class BaseRepository(Generic[ModelType]):

  def __init__(self, session: AsyncSession, model: type[ModelType]):
    self.session = session
    self.model = model

  async def get_by_id(self, record_id: UUID) -> ModelType | None:
    ...

  async def get_all(
      self, *, offset: int = 0, limit: int = 100
  ) -> list[ModelType]:
    ...

  async def create(self, instance: ModelType) -> ModelType:
    ...

  async def update(self, instance: ModelType) -> ModelType:
    ...

  async def delete(self, instance: ModelType) -> None:
    ...
```

---

## 3. Domain Repositories

### 3.1 `TenantRepository`
Located at `apps/api/src/menu_it/repositories/tenants.py`:
- `get_by_slug(slug: str) -> Tenant | None`
- `slug_exists(slug: str) -> bool`

### 3.2 `RestaurantRepository`
Located at `apps/api/src/menu_it/repositories/restaurants.py`:
- `get_by_tenant_and_slug(tenant_id: UUID, slug: str) -> Restaurant | None`
- `list_by_tenant(tenant_id: UUID, *, offset: int = 0, limit: int = 100) -> list[Restaurant]`
- `slug_exists_for_tenant(tenant_id: UUID, slug: str) -> bool`

---

## 4. Usage Example

```python
async def sample_handler(session: AsyncSession = Depends(get_db_session)):
  repo = TenantRepository(session)
  tenant = await repo.get_by_slug("demo-slug")
  return tenant
```
