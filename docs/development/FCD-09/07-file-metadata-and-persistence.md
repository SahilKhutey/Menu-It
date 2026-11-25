# FCD-09 §07 — File Metadata & Persistence

## 1. Relational Schema Design

File metadata is persisted in the PostgreSQL `files` table managed via Alembic migration `0006_files_and_notifications.py`:

```sql
CREATE TABLE files (
    id UUID PRIMARY KEY,
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    uploaded_by UUID REFERENCES users(id) ON DELETE SET NULL,
    original_filename VARCHAR(180) NOT NULL,
    storage_key VARCHAR(512) NOT NULL UNIQUE,
    mime_type VARCHAR(120) NOT NULL,
    size_bytes BIGINT NOT NULL,
    checksum_sha256 VARCHAR(64) NOT NULL,
    visibility VARCHAR(32) NOT NULL DEFAULT 'tenant_private',
    status VARCHAR(20) NOT NULL DEFAULT 'stored',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMPTZ NULL
);
```

---

## 2. Row-Level Security (RLS) Policy

PostgreSQL Row-Level Security enforces tenant isolation directly in the database engine:

```sql
ALTER TABLE files ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation_files ON files
FOR ALL
USING (
    visibility = 'public'
    OR (
        organization_id IS NOT NULL
        AND organization_id = NULLIF(current_setting('app.current_organization_id', true), '')::uuid
    )
)
WITH CHECK (
    organization_id IS NOT NULL
    AND organization_id = NULLIF(current_setting('app.current_organization_id', true), '')::uuid
);
```

---

## 3. Partial Failure Recovery

If database insertion fails after an object has already been written to disk or object storage, `FileService` catches the exception and immediately invokes `storage.delete(key)` to prevent storage leaks and orphaned files.
