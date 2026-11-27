# FCD-06 §15 — Tenant Ownership & Row-Level Security

## 1. Dual-Defense Multi-Tenancy

Menu-It enforces tenant isolation across two distinct layers:

### 1.1 Composite Foreign Key Enforcement (Data Layer)
`restaurant_profiles` binds to `restaurants` via a composite foreign key:
```sql
CONSTRAINT fk_restaurant_profiles_org_restaurant
FOREIGN KEY (organization_id, restaurant_id)
REFERENCES restaurants (organization_id, id)
ON DELETE CASCADE;
```
This physically prevents a restaurant profile from belonging to Organization A while referencing a restaurant belonging to Organization B.

### 1.2 PostgreSQL Row-Level Security (RLS)
The database engine enforces table-level filtering on all operations:
```sql
ALTER TABLE restaurant_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE restaurant_profiles FORCE ROW LEVEL SECURITY;

CREATE POLICY restaurant_profiles_tenant_isolation ON restaurant_profiles
USING (
    organization_id = NULLIF(
        current_setting('app.current_organization_id', true), ''
    )::uuid
)
WITH CHECK (
    organization_id = NULLIF(
        current_setting('app.current_organization_id', true), ''
    )::uuid
);
```

### 1.3 Repository & Service Scope (Application Layer)
Application services and repository queries enforce:
1. `assert_restaurant_belongs_to_organization()` validation.
2. `get_by_restaurant_id(restaurant_id, organization_id)` scoping.
Any cross-tenant attempt returns `None` or raises `BusinessRuleViolationError`.
