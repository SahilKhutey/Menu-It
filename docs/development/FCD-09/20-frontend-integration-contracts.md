# FCD-09 §20 — Frontend Integration Contracts

## 1. Shared TypeScript Contracts

The frontend ecosystem consumes platform models via `@menu-it/shared-types`:

### File Contracts (`packages/shared-types/src/platform/files.ts`)
```typescript
export type FileVisibility = 'public' | 'tenant_private' | 'user_private' | 'platform_private';
export type FileStatus = 'pending' | 'stored' | 'rejected' | 'failed' | 'deleted';

export interface FileMetadata {
  id: string;
  filename: string;
  mime_type: string;
  size_bytes: number;
  visibility: FileVisibility;
  status: FileStatus;
  created_at: string;
}
```

### Notification Contracts (`packages/shared-types/src/platform/notifications.ts`)
```typescript
export type NotificationChannel = 'email' | 'in_app';
export type NotificationStatus = 'pending' | 'accepted' | 'sent' | 'delivered' | 'failed' | 'cancelled';

export interface InAppNotification {
  id: string;
  type: string;
  title: string;
  body: string;
  read_at: string | null;
  created_at: string;
}
```

---

## 2. API Compatibility

All frontend requests map directly to FCD-07 `APIResponse<T>` envelopes. Internal storage keys and sensitive infrastructure details are never present in client contracts.
