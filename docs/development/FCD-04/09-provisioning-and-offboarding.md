# FCD-04 — Tenant Provisioning & Offboarding Primitives

## 1. Atomic Organization Provisioning

Tenant onboarding involves creating multiple related database records across tables (`organizations`, `organization_memberships`, `restaurants`, `restaurant_memberships`, and `organization_audit_events`).

If any step fails (e.g. duplicate slug, database constraint violation, network glitch), partial tenant state must never remain orphaned in the database.

### `OrganizationProvisioningService`
The provisioning service runs entirely within an explicit atomic transaction:

```mermaid
sequenceDiagram
    autonumber
    actor Client
    participant Service as OrganizationProvisioningService
    participant Session as AsyncSession
    participant DB as PostgreSQL Database

    Client->>Service: provision_organization(name, slug, owner_user_id, ...)
    Service->>Session: session.begin()
    Service->>DB: Check slug availability (organizations)
    alt Slug exists
        DB-->>Service: Conflict
        Service-->>Client: ResourceConflictError (409)
    end
    Service->>DB: INSERT INTO organizations (status='provisioning')
    Service->>DB: INSERT INTO organization_memberships (role='owner', status='active')
    opt Initial restaurant requested
        Service->>DB: INSERT INTO restaurants (status='active')
        Service->>DB: INSERT INTO restaurant_memberships (role='manager')
    end
    Service->>DB: INSERT INTO organization_audit_events (event_type='organization.provisioned')
    Service->>DB: UPDATE organizations SET status='active'
    Service->>Session: Transaction Commit
    Service-->>Client: (Organization, OrganizationMembership, Restaurant)
```

---

## 2. Offboarding & Data Deletion Primitives

Offboarding proceeds through structured phases:
1. **Initiate Offboarding**: Transition organization to `OFFBOARDING`. Prevents all modifications and new orders while allowing export jobs.
2. **Data Retention Window**: 30-day grace period where tenant administrators can request JSON/CSV data archives.
3. **Deactivation**: Transition to `DEACTIVATED`. API access is revoked; external integrations and webhooks are disabled.
4. **Purge / Scrub**: Scheduled batch workers sanitize personally identifiable customer data (PII) in compliance with privacy regulations.
