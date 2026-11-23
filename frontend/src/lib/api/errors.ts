/**
 * ModularMenu — API Error Helpers & UI Mapping (ARC-07 §5.5, §13.6).
 */
import { ApiError, ProblemDetails } from "./client";

export type ErrorSeverity = "critical" | "warning" | "info";

export interface FormErrorMapping {
  generalMessage: string;
  fieldErrors: Record<string, string>;
}

export function mapApiErrorToForm(error: unknown): FormErrorMapping {
  if (error instanceof ApiError) {
    const fieldErrors: Record<string, string> = {};

    if (error.details && Array.isArray(error.details)) {
      for (const item of error.details) {
        if (item.field && item.message) {
          fieldErrors[item.field] = item.message;
        } else if (item.loc && item.msg) {
          const field = Array.isArray(item.loc) ? item.loc.join(".") : String(item.loc);
          fieldErrors[field] = item.msg;
        }
      }
    }

    return {
      generalMessage: error.message,
      fieldErrors,
    };
  }

  return {
    generalMessage: error instanceof Error ? error.message : "An unexpected error occurred",
    fieldErrors: {},
  };
}

export function isConflictError(error: unknown): boolean {
  return error instanceof ApiError && error.status === 409;
}

export function isAuthError(error: unknown): boolean {
  return error instanceof ApiError && (error.status === 401 || error.status === 403);
}

export function isRateLimitError(error: unknown): boolean {
  return error instanceof ApiError && error.status === 429;
}
