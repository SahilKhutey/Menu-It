# FCD-07 §18 — Database Schema Changes & Alembic Migrations

## 1. Migration Overview

Phase FCD-07 introduces Alembic revision `0005_idempotency_records`:
- **Revision ID:** `0005_idempotency_records`
- **Down Revision:** `0004_restaurant_profiles`
- **File:** `apps/api/alembic/versions/0005_create_idempotency_records.py`

---

## 2. Table Definition & Indexes

```sql
CREATE TABLE idempotency_records (
    id UUID PRIMARY KEY,
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    actor_id UUID REFERENCES users(id) ON DELETE CASCADE,
    key VARCHAR(128) NOT NULL,
    request_hash VARCHAR(64) NOT NULL,
    response_status INTEGER NOT NULL,
    response_body JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    CONSTRAINT uq_idempotency_org_actor_key UNIQUE (organization_id, actor_id, key)
);

CREATE INDEX ix_idempotency_records_org_id ON idempotency_records(organization_id);
CREATE INDEX ix_idempotency_records_actor_id ON idempotency_records(actor_id);
CREATE INDEX ix_idempotency_records_key ON idempotency_records(key);
CREATE INDEX ix_idempotency_records_org_key ON idempotency_records(organization_id, key);
CREATE INDEX ix_idempotency_records_expires_at ON idempotency_records(expires_at);
```

---

## 3. Row-Level Security (RLS) Policy

On PostgreSQL targets, Row-Level Security is enabled and enforced:

```sql
ALTER TABLE idempotency_records ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation_idempotency_records ON idempotency_records
FOR ALL
USING (
    organization_id = NULLIF(current_setting('app.current_organization_id', true), '')::uuid
)
WITH CHECK (
    organization_id = NULLIF(current_setting('app.current_organization_id', true), '')::uuid
);
```

This guarantees tenant boundary integrity even for network retry tokens.
