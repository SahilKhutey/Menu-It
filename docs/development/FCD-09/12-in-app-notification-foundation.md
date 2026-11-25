# FCD-09 §12 — In-App Notification Foundation

## 1. Schema & Persistence

In-app notifications are stored in the PostgreSQL `notifications` table:

```sql
CREATE TABLE notifications (
    id UUID PRIMARY KEY,
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    recipient_user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type VARCHAR(64) NOT NULL,
    title VARCHAR(256) NOT NULL,
    body VARCHAR(1024) NOT NULL,
    payload JSONB NULL,
    read_at TIMESTAMPTZ NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMPTZ NULL
);
```

---

## 2. Tenant & Recipient Isolation

A user can only query their own notifications (`recipient_user_id == current_user.id`).
If an active organization context is present, notifications are optionally filtered by `organization_id` while still permitting platform-wide notifications (`organization_id IS NULL`).

---

## 3. Read/Unread State Transitions

When a user views a notification, a `PATCH /api/v1/notifications/{id}/read` request populates `read_at = CURRENT_TIMESTAMP`. Unread filters (`unread_only=true`) check for `read_at IS NULL`.
