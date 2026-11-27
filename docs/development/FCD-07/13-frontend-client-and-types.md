# FCD-07 §13 — Frontend HTTP Client & Shared Type Contracts

## 1. Shared TypeScript Package (`@menu-it/shared-types`)

All API contract interfaces are published in `@menu-it/shared-types` and consumed by both `apps/web` (customer and staff portal) and `apps/admin` (platform back-office):

- `APIResponse<T>`: Universal response envelope with `meta: RequestMetadata`.
- `APIError`: Standard error structure with `code: ErrorCode`, `message`, and `details`.
- `ErrorCode`: Union type of all valid backend error codes (`VALIDATION_ERROR`, `RESOURCE_CONFLICT`, etc.).
- `PaginationMeta` & `PaginatedData<T>`: Standard pagination representation.
- `RestaurantSummary` & `CreateRestaurantRequest`: Domain DTO contracts.

---

## 2. Universal API Client (`apiRequest`)

Implemented in `apps/web/src/services/api-client.ts` and `apps/admin/src/services/api-client.ts`:

```typescript
export interface APIRequestOptions extends RequestInit {
  idempotencyKey?: string;
  token?: string;
}

export async function apiRequest<T>(
  path: string,
  options?: APIRequestOptions
): Promise<APIResponse<T>>;
```

### Key Capabilities
1. **HTTP 204 No Content Handling:** Gracefully constructs `{ success: true, data: null, error: null, meta: ... }` without triggering JSON parsing errors.
2. **Idempotency Propagation:** Automatically maps `idempotencyKey` option to `Idempotency-Key` HTTP header.
3. **Bearer Token Injection:** Automatically attaches `Authorization: Bearer <token>` when supplied.
4. **Error Transformation:** Non-2xx HTTP responses throw `APIClientError` carrying `status`, `code`, `message`, `requestId`, and structured `details`.
5. **JSON Fallback:** Non-JSON server responses (e.g. gateway 502/504) produce clean `APIClientError` with status code and generic message.
