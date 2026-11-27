# FCD-15 — 13 Security & Tenant Isolation

Enforced via FCD-05 RBAC permissions, `organization_id` + `restaurant_id` + `branch_id` scoped queries, composite foreign keys, PostgreSQL RLS policies, validated `HexColor` tokens (no arbitrary CSS injection), and strict public DTO allowlisting.
