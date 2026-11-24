# FCD-06 §19 — Architecture Decisions Records (ADRs)

## ADR-0010: Pure Zero-Dependency Domain Layer
- **Status**: Accepted
- **Context**: Future Menu-It modules (Menu, Ordering, Kitchen, Inventory, Billing) must rely on shared business models and value objects without coupling to specific ORMs or web frameworks.
- **Decision**: `menu_it.domain` must have zero imports from `fastapi`, `sqlalchemy`, or `pydantic`. All persistence interfaces are defined as `typing.Protocol` ports.
- **Consequences**: Fast unit test execution (< 1s), zero framework lock-in, and pure invariant enforcement.

## ADR-0011: Composite Foreign Key for Subordinate Tenant Entities
- **Status**: Accepted
- **Context**: In multi-tenant systems, single-column foreign keys (`restaurant_id`) allow logical leaks if a child record references a parent owned by a different organization.
- **Decision**: All subordinate tenant tables must use a composite foreign key `(organization_id, parent_id) -> parent(organization_id, id)`.
- **Consequences**: Database engine physically rejects cross-tenant references at the storage level.

## ADR-0012: Operating Hours Timeline Intervals for Overnight Spans
- **Status**: Accepted
- **Context**: Restaurant operating shifts frequently span across midnight (e.g. 21:00 to 02:00), breaking simple `open < close` comparisons.
- **Decision**: Model overnight shifts as two half-open intervals on a single day timeline (`[opens_at, 23:59:59.999999]` and `[00:00:00, closes_at]`). Overlap is computed via interval intersection across all range pairs.
- **Consequences**: Accurate, bug-free schedule validation and overlap detection without date-dependent math.
