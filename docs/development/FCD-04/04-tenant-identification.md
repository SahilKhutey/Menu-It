# FCD-04 — Tenant Identification & Resolution

## 1. Principles of Tenant Identification

In multi-tenant SaaS engineering, confusing *target identification* with *access authorization* is the leading cause of security vulnerabilities (BOLA/IDOR). Menu-It enforces strict architectural separation:

1. **Target Organization**: Identifies *which* organization resource is being requested (e.g. from `/organizations/{organization_id}/current`).
2. **Authenticated Principal**: Identifies *who* is making the request, extracted from verified credentials.
3. **Tenant Resolver**: Queries the persistent store to verify whether the principal has an active membership in the target organization before synthesizing a `TenantContext`.

---

## 2. Rejection of Untrusted Tenant Headers

Client applications frequently attempt to send headers such as `X-Tenant-ID` or `X-Organization-ID`. In Menu-It:
- **No tenant identity header is trusted from the client.**
- Any attempt to bypass membership checks using custom headers is ignored.
- Only the server-verified identity (`AuthenticatedPrincipal`) coupled with database membership verification can establish a tenant context.

---

## 3. The `TenantResolver` Pipeline

The `TenantResolver` executes the resolution logic deterministically:

```python
class TenantResolver:
    async def resolve(
        self,
        principal: AuthenticatedPrincipal,
        organization_id: UUID,
        restaurant_id: UUID | None = None,
        correlation_id: str | None = None,
    ) -> TenantContext: ...
```

### Verification Steps
1. **Principal Verification**: Ensures `principal.is_authenticated` is `True` and `principal.user_id` is a valid UUID.
2. **Organization Status**: Loads `Organization` by `organization_id`. Rejects non-existent organizations with `TenantNotFoundError` (translated to HTTP 404 to avoid leaking existence). Rejects non-active organizations (`SUSPENDED`, `OFFBOARDING`, `DEACTIVATED`) with `TenantSuspendedError` (HTTP 403).
3. **Membership Status**: Queries `OrganizationMembership` for `(organization_id, user_id)`. Rejects non-members with `TenantNotFoundError` (HTTP 404) to prevent resource enumeration. Rejects non-active memberships (`PENDING`, `SUSPENDED`, `REVOKED`) with `TenantAccessDeniedError` (HTTP 403).
4. **Restaurant Scope Verification**:
   - If `restaurant_id` is provided:
     - Verifies restaurant belongs to `organization_id` and has status `ACTIVE`.
     - If the user is `OWNER` or `ADMIN`, access is automatically permitted by organization authority.
     - If the user is `MEMBER`, queries `RestaurantMembership`. If absent, raises `RestaurantAccessDeniedError` (HTTP 403).
5. **Context Construction**: Returns an immutable `TenantContext` containing verified IDs and roles.
