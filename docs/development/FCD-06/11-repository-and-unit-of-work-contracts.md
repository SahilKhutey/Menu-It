# FCD-06 §11 — Repository & Unit of Work Contracts

## 1. Domain Ports (Structural Subtyping)

The domain specifies persistence contracts as Python `typing.Protocol` interfaces in `apps/api/src/menu_it/domain/ports/`:

### 1.1 `RestaurantProfileRepository`
```python
class RestaurantProfileRepository(Protocol):
    async def get_by_id(self, profile_id: UUID) -> RestaurantProfile | None: ...
    async def get_by_restaurant_id(
        self, restaurant_id: UUID, organization_id: UUID
    ) -> RestaurantProfile | None: ...
    async def save(self, profile: RestaurantProfile) -> None: ...
```

### 1.2 `MenuItUnitOfWork`
```python
class MenuItUnitOfWork(Protocol):
    restaurant_profiles: RestaurantProfileRepository

    async def __aenter__(self) -> Self: ...
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None: ...
    async def commit(self) -> None: ...
    async def rollback(self) -> None: ...
```

### 1.3 `DomainEventPublisher`
```python
class DomainEventPublisher(Protocol):
    async def publish(self, events: list[DomainEvent]) -> None: ...
```

## 2. Infrastructure Separation

Because these interfaces reside in `domain.ports`, application services can be tested against in-memory doubles without a running PostgreSQL database or Docker daemon.
