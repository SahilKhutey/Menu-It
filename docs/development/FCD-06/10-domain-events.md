# FCD-06 §10 — Domain Events Specification

## 1. Event Model Base

Defined in `apps/api/src/menu_it/domain/base/domain_event.py`:

```python
@dataclass(frozen=True, slots=True)
class DomainEvent:
    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    event_type: str = "domain.event"
    schema_version: int = 1
    organization_id: UUID | None = None
    restaurant_id: UUID | None = None
    actor_user_id: UUID | None = None
    correlation_id: str | None = None
    payload: dict[str, Any] = field(default_factory=dict)
```

## 2. Emitted Domain Events

Located in `apps/api/src/menu_it/domain/restaurant/events.py`:

### 2.1 `RestaurantProfileUpdated`
Emitted whenever restaurant profile attributes are initialized or modified.
- `event_type`: `"restaurant.profile_updated"`
- `profile_id: UUID`
- `changed_fields: tuple[str, ...]` (e.g. `("__created__",)`, `("public_name",)`, `("schedule",)`)
- `version: int`

### 2.2 `RestaurantStatusChanged`
Emitted when a restaurant transitions lifecycle status.
- `event_type`: `"restaurant.status_changed"`
- `previous_status: str`
- `new_status: str`
- `reason: str | None`

### 2.3 `RestaurantOperatingHoursUpdated`
Emitted specifically when weekly operating hours are updated, allowing downstream kitchen, reservation, and menu services to re-evaluate availability.
- `event_type`: `"restaurant.operating_hours_updated"`
- `profile_id: UUID`
- `version: int`

## 3. Publication Pattern

Aggregate roots record events internally during mutation methods. Application services collect recorded events after persistence flushes and forward them to `DomainEventPublisher` ports for asynchronous dispatch.
