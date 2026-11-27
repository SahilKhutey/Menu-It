# FCD-06 §02 — Domain Design Principles

## 1. Tactical DDD Patterns

Menu-It implements core tactical Domain-Driven Design (DDD) patterns tailored for modern Python 3.12+:

### 1.1 Value Objects
- **Immutability**: Declared with `@dataclass(frozen=True, slots=True)`. Once created, internal fields cannot be reassigned.
- **Structural Equality**: Equality is derived from all encapsulated properties, not an identifier.
- **Self-Validation**: The `__post_init__` lifecycle validates all domain constraints (e.g. ISO 4217 currency codes, RFC email validation, IANA timezone names). Any violation immediately raises `ValidationDomainError`.
- **Side-Effect-Free Operations**: Calculations (such as `Money.add()` or `TimeRange.overlaps_with()`) return fresh instances or boolean results without mutating existing state.

### 1.2 Entities
- **Identity-Based Equality**: Two entities are equal if and only if they share the exact same runtime type and `id: UUID`, irrespective of attribute mutations.
- **Hash Stability**: `__hash__` is stable across mutations, returning `hash((type(self), self.id))`.

### 1.3 Aggregate Roots
- **Transactional Consistency Boundary**: Subordinate entities and value objects are manipulated exclusively through the aggregate root.
- **Encapsulated State Mutations**: Attributes are modified through explicit domain methods (e.g., `update_public_name()`, `update_schedule()`) that validate invariants, update modification timestamps, advance optimistic locking versions, and record domain events.
- **Event Accumulation**: Aggregate roots collect uncommitted domain events internally via `self.record_event()` and drain them atomically via `self.collect_events()`.

## 2. Invariant Protection

Invariants are business rules that must remain true at all times within a boundary:
1. An aggregate cannot exist in an invalid state.
2. Monetary values cannot mix currencies or use floating-point types.
3. Operating hours cannot overlap on the same business day.
4. Tenant resources must strictly belong to the active organization.
