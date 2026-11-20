# 04 — Tenant Context Resolution

## 1. The Immutable TenantContext

```python
@dataclass(frozen=True)
class TenantContext:
    user_id: UUID
    organization_id: UUID
    membership_id: UUID
    organization_role: str
    allowed_restaurant_ids: Optional[frozenset[UUID]] = None
    request_id: str = ""
    authentication_method: str = "bearer_jwt"
```

## 2. Resolution Lifecycle

1. **Bearer Token Authentication:** The API Gateway / FastAPI middleware verifies JWT signature, expiry, and extracts `user_id`.
2. **Tenant Selector Ingestion:** The client specifies target organization via `X-Organization-Id` header or route parameter.
3. **Membership Verification:** `TenantResolver` validates that `(user_id, target_organization_id)` exists in active memberships.
4. **Suspension Check:** If the organization is suspended, management operations are denied (`TenantSuspendedException`).
5. **Context Instantiation:** An immutable `TenantContext` is constructed and attached to the request state.
6. **Propagation:** Context is explicitly passed into application use cases, command buses, and transaction scopes.
