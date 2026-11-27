# FCD-06 §16 — Domain Testing Strategy

## 1. Testing Pyramid

Menu-It follows a rigorous testing pyramid:

```
          /  E2E / System  \
         /------------------\
        /    Integration     \     (66 tests)
       /----------------------\
      /  API Transport & DTO   \   (9 tests)
     /--------------------------\
    /      Pure Domain Unit      \ (56 tests)
   +------------------------------+
```

## 2. Test Suites

### 2.1 Pure Domain Tests (`apps/api/tests/unit/domain/` & `unit/value_objects/`)
- Require zero database connections, zero HTTP servers, zero docker containers.
- Execute in under 1 second (56 tests in 0.56s).
- Verify value object parsing, currency math, phone number normalization, overnight hour overlap detection, aggregate mutation events, and lifecycle rules.

### 2.2 API Contract Tests (`apps/api/tests/contract/`)
- Verify Pydantic schema validation, pagination query bounds (1 <= page_size <= 100), and serialization format.

### 2.3 Integration Tests (`apps/api/tests/integration/`)
- Verify `SQLAlchemyRestaurantProfileRepository` persistence, mapper bi-directional conversion, optimistic concurrency locking, service execution, event publishing, and tenant isolation.
