# FCD-04 — Membership and Restaurant Assignment Models

## 1. Membership Architecture

User authorization within the Menu-It multi-tenant platform is decoupled from user authentication. A verified user may hold memberships across multiple organizations, but each request executes strictly within the context of a single active membership.

---

## 2. Organization Memberships

The `organization_memberships` table establishes a user's relationship with an organization.

### Table Schema
```sql
CREATE TABLE organization_memberships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    user_id UUID NOT NULL,
    role VARCHAR(32) NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    CONSTRAINT uq_org_memberships_org_user UNIQUE (organization_id, user_id)
);

CREATE INDEX ix_org_memberships_user ON organization_memberships (user_id);
```

### Roles (`OrganizationRole`)
- **`owner`**: Complete authority over the organization, billing, restaurants, staff, and lifecycle states.
- **`admin`**: Full administrative privileges over restaurants and staff; excluded from transfer of ownership and organization deletion.
- **`member`**: Standard organization member; permissions scoped to specific restaurant assignments.
- **`billing_admin`**: Specialized role limited to invoices, subscriptions, and payment methods.

### Statuses (`MembershipStatus`)
- **`pending`**: Invitation issued, awaiting acceptance or verification.
- **`active`**: Fully operational membership granting access according to role.
- **`suspended`**: Temporarily blocked by organization administrators.
- **`revoked`**: Inactive membership (offboarded user).

---

## 3. Restaurant Memberships & Composite Foreign Keys

Staff members with fine-grained restaurant-level permissions receive assignments via `restaurant_memberships`.

### Composite Integrity Constraint
To eliminate the risk of assigning a user to a restaurant belonging to a different organization, Menu-It implements a **composite foreign key**:

```sql
CREATE TABLE restaurant_memberships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL,
    restaurant_id UUID NOT NULL,
    user_id UUID NOT NULL,
    role VARCHAR(32) NOT NULL DEFAULT 'staff',
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    CONSTRAINT uq_restaurant_memberships_rest_user UNIQUE (restaurant_id, user_id),
    CONSTRAINT fk_restaurant_memberships_org_rest
        FOREIGN KEY (organization_id, restaurant_id)
        REFERENCES restaurants(organization_id, id)
        ON DELETE CASCADE
);
```

This guarantees that a restaurant membership cannot physically reference a `restaurant_id` whose `organization_id` does not match the membership's `organization_id`.
