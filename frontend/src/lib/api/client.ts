/**
 * ModularMenu Shared API Client (ARC-03 §3.3, ARC-07 §13.1, §13.2).
 * Handles:
 * - Base URL resolution & validation
 * - Request correlation ID tracking (X-Request-ID)
 * - Cookie sessions (credentials: "include") & Bearer tokens
 * - CSRF token injection (X-CSRF-Token)
 * - RFC 7807 / RFC 9457 Problem Details error normalization
 * - Safe JSON/Non-JSON response parsing
 */

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  "http://127.0.0.1:8000/api/v1";

export interface ProblemDetails {
  type: string;
  title: string;
  status: number;
  detail?: string;
  instance?: string;
  code?: string;
  request_id?: string;
  invalid_params?: any[];
  errors?: any[];
}

export class ApiError extends Error {
  constructor(
    public status: number,
    public code: string,
    message: string,
    public details?: any[],
    public instance?: string,
    public requestId?: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

export interface ApiRequestOptions extends RequestInit {
  token?: string;
  correlationId?: string;
  csrfToken?: string;
}

export async function apiRequest<T>(
  path: string,
  options: ApiRequestOptions = {},
): Promise<T> {
  const { token, correlationId, csrfToken, headers: customHeaders, ...fetchInit } = options;
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  const url = `${API_BASE_URL}${normalizedPath}`;

  const headers: Record<string, string> = {
    Accept: "application/json, application/problem+json",
    ...(correlationId ? { "X-Request-ID": correlationId } : {}),
    ...(csrfToken ? { "X-CSRF-Token": csrfToken } : {}),
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...(customHeaders as Record<string, string>),
  };

  if (fetchInit.body && !(fetchInit.body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
  }

  try {
    const response = await fetch(url, {
      ...fetchInit,
      headers,
      credentials: "include", // For session cookies (ARC-07 §6.1, §13.2)
    });

    if (!response.ok) {
      let errorBody: ProblemDetails | any = {};
      try {
        errorBody = await response.json();
      } catch {
        errorBody = {
          title: response.statusText || "Request failed",
          detail: `HTTP ${response.status}: Failed to execute request on ${path}`,
          status: response.status,
        };
      }

      throw new ApiError(
        response.status,
        errorBody.code || errorBody.title || "REQUEST_FAILED",
        errorBody.detail || errorBody.message || "An unexpected API error occurred",
        errorBody.errors || errorBody.invalid_params || errorBody.details,
        errorBody.instance || path,
        errorBody.request_id,
      );
    }

    if (response.status === 204) {
      return undefined as T;
    }

    return (await response.json()) as T;
  } catch (error: any) {
    if (error instanceof ApiError) {
      throw error;
    }
    throw new ApiError(
      503,
      "NETWORK_ERROR",
      `Unable to communicate with ModularMenu API server at ${url}: ${error.message}`,
    );
  }
}

// Alias matching ARC-07 §13.2 specification
export const apiFetch = apiRequest;
