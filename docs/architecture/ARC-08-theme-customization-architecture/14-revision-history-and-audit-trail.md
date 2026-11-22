# ARC-08 §14 — Revision History & Audit Trail

## 1. Database Model (`CustomizationRevision`)
```sql
CREATE TABLE customization_revisions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customization_id UUID NOT NULL REFERENCES menu_customizations(id) ON DELETE CASCADE,
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    menu_id UUID NOT NULL REFERENCES menus(id) ON DELETE CASCADE,
    revision INTEGER NOT NULL,
    configuration JSONB NOT NULL,
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_customization_revision UNIQUE (customization_id, revision)
);
```

## 2. Audit Invariants
- Revisions are append-only and strictly immutable.
- Restoring revision $k$ does not alter or delete history; it appends revision $N+1$ with payload copied from $k$ and metadata tag `"restored_from": k`.
