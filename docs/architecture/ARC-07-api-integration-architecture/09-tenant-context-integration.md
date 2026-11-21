# 09. Tenant Context Integration

## 1. Server-Derived Tenant Context
The `TenantContext` is resolved exclusively by server-side authentication and database membership records.
```python
@dataclass(frozen=True)
class TenantContext:
    user_id: UUID
    organization_id: UUID
    membership_id: UUID
    organization_role: str
    allowed_restaurant_ids: Optional[frozenset[UUID]] = None
    request_id: str = ""
    authentication_method: str = "session"
```
## 2. Header Policy
`X-Organization-ID` is treated strictly as a selector among memberships already possessed by the user. If the user does not possess active membership in the selected organization, access is immediately rejected (403 Forbidden).
