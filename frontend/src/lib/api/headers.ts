/**
 * ModularMenu — API Headers & Correlation Helpers (ARC-07 §3.5).
 */

export function createApiHeaders(options: {
  correlationId?: string;
  csrfToken?: string;
  idempotencyKey?: string;
  ifMatch?: string;
}): Record<string, string> {
  const headers: Record<string, string> = {
    Accept: "application/json",
  };

  if (options.correlationId) {
    headers["X-Request-ID"] = options.correlationId;
  }
  if (options.csrfToken) {
    headers["X-CSRF-Token"] = options.csrfToken;
  }
  if (options.idempotencyKey) {
    headers["Idempotency-Key"] = options.idempotencyKey;
  }
  if (options.ifMatch) {
    headers["If-Match"] = options.ifMatch;
  }

  return headers;
}
