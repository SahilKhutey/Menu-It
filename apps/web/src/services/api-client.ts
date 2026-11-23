import type { APIResponse } from '@menu-it/shared-types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:8000/api/v1';

export class APIClientError extends Error {
  constructor(
    message: string,
    public readonly status: number,
    public readonly code: string,
  ) {
    super(message);
    this.name = 'APIClientError';
  }
}

export async function apiRequest<T>(path: string, init?: RequestInit): Promise<APIResponse<T>> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      Accept: 'application/json',
      ...init?.headers,
    },
    cache: 'no-store',
  });

  const payload = await response.json().catch(() => null);

  if (!response.ok) {
    const message = payload?.error?.message ?? 'The API request failed.';
    const code = payload?.error?.code ?? 'API_REQUEST_FAILED';
    throw new APIClientError(message, response.status, code);
  }

  if (
    !payload ||
    typeof payload.success !== 'boolean' ||
    payload.success !== true ||
    !payload.meta?.request_id
  ) {
    throw new APIClientError(
      'The API returned an invalid response.',
      response.status,
      'INVALID_API_RESPONSE',
    );
  }

  return payload as APIResponse<T>;
}
