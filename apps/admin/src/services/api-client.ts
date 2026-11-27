import type { APIErrorDetail, APIResponse, ErrorCode } from '@menu-it/shared-types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:8000/api/v1';

export interface APIRequestOptions extends RequestInit {
  idempotencyKey?: string;
  token?: string;
}

export class APIClientError extends Error {
  constructor(
    message: string,
    public readonly status: number,
    public readonly code: ErrorCode | string,
    public readonly requestId?: string | null,
    public readonly details?: APIErrorDetail[],
  ) {
    super(message);
    this.name = 'APIClientError';
  }
}

export async function apiRequest<T>(
  path: string,
  options?: APIRequestOptions,
): Promise<APIResponse<T>> {
  const { idempotencyKey, token, headers: customHeaders, ...restInit } = options ?? {};

  const headers: Record<string, string> = {
    Accept: 'application/json',
    ...(customHeaders as Record<string, string>),
  };

  if (idempotencyKey) {
    headers['Idempotency-Key'] = idempotencyKey;
  }

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  if (restInit.body && typeof restInit.body === 'string' && !headers['Content-Type']) {
    headers['Content-Type'] = 'application/json';
  }

  const url = path.startsWith('http') ? path : `${API_BASE_URL}${path}`;

  const response = await fetch(url, {
    ...restInit,
    headers,
    cache: 'no-store',
  });

  const responseRequestId = response.headers.get('X-Request-ID');

  if (response.status === 204) {
    return {
      success: true,
      data: null,
      error: null,
      meta: {
        request_id: responseRequestId ?? '00000000-0000-0000-0000-000000000000',
        timestamp: new Date().toISOString(),
      },
    };
  }

  const payload = await response.json().catch(() => null);

  if (!response.ok) {
    const message = payload?.error?.message ?? `API request failed with status ${response.status}.`;
    const code = payload?.error?.code ?? 'API_REQUEST_FAILED';
    const details = payload?.error?.details ?? [];
    const requestId = payload?.meta?.request_id ?? responseRequestId;
    throw new APIClientError(message, response.status, code, requestId, details);
  }

  if (!payload || typeof payload.success !== 'boolean' || payload.success !== true) {
    throw new APIClientError(
      'The API returned an unexpected or malformed response envelope.',
      response.status,
      'INVALID_API_RESPONSE',
      responseRequestId,
    );
  }

  return payload as APIResponse<T>;
}
