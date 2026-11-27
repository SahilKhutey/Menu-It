# FCD-02 — Shared Runtime & Application Contracts

## 1. Overview
Cross-application communication between Next.js frontends and FastAPI backends is standardized through shared contract interfaces.

## 2. Package `@menu-it/shared-types`
Located at `packages/shared-types/`:
```typescript
export type UUID = string;

export interface RequestMetadata {
  request_id: UUID;
  timestamp: string;
}

export interface APIError {
  code: string;
  message: string;
  details: Array<Record<string, unknown>>;
}

export interface APIResponse<T> {
  success: boolean;
  data: T | null;
  error: APIError | null;
  meta: RequestMetadata;
}
```

## 3. Frontend API Client (`api-client.ts`)
- Generic type-safe function `apiRequest<T>(path: string, init?: RequestInit): Promise<APIResponse<T>>`.
- Validates enveloped response format: verifies `payload.success === true` and `payload.meta.request_id` exists.
- Rejects invalid envelopes with typed `APIClientError`.

## 4. Operational Health Client (`health-service.ts`)
- Separate client for un-enveloped operational health endpoints (`/health`).
- Prevents coupling operational monitoring with business payload formats.
