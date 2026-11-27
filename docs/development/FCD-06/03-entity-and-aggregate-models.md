# FCD-06 §03 — Entity & Aggregate Models

## 1. Domain Base Primitives

Located in `apps/api/src/menu_it/domain/base/`:

### 1.1 `Entity[T]`
```python
@dataclass(eq=False)
class Entity(Generic[T]):
    id: UUID

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Entity):
            return NotImplemented
        return type(self) is type(other) and self.id == other.id

    def __hash__(self) -> int:
        return hash((type(self), self.id))
```

### 1.2 `AggregateRoot`
```python
@dataclass(eq=False)
class AggregateRoot(Entity):
    _domain_events: list[DomainEvent] = field(default_factory=list, init=False, repr=False, compare=False)

    def record_event(self, event: DomainEvent) -> None:
        self._domain_events.append(event)

    def collect_events(self) -> list[DomainEvent]:
        events = list(self._domain_events)
        self._domain_events.clear()
        return events
```

## 2. Strong Identifiers

Located in `apps/api/src/menu_it/domain/shared/identifiers.py`:
- `OrganizationId`: Strongly-typed alias / value representation for tenant boundaries.
- `RestaurantId`: Restaurant location identifier.
- `UserId`: Platform user identity reference.
- `DomainEventId`: Unique event identity.

## 3. Domain Exception Hierarchy

Defined in `apps/api/src/menu_it/domain/base/errors.py`:
- `DomainError`: Base root for all domain errors.
  - `ValidationDomainError`: Malformed format, missing required attribute, or out-of-range value.
  - `EntityNotFoundError`: Aggregate root or entity reference does not exist.
  - `InvalidStateTransitionError`: Prohibited lifecycle transition attempted.
  - `BusinessRuleViolationError`: Core invariant broken (e.g. currency mismatch, overlapping shift).
  - `ConcurrencyConflictError`: Stale optimistic locking version encountered.
