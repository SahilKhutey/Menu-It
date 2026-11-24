/**
 * Common shared contracts and types across Menu-It frontend and backend (FCD-06 §13).
 */

export type UUID = string;
export type ISO8601String = string;

export interface RequestMetadata {
  request_id: UUID;
  timestamp: ISO8601String;
}

export interface MoneyDTO {
  amount: string;
  currency: string;
}

export interface AddressDTO {
  line_1: string;
  locality: string;
  country_code: string;
  line_2?: string | null;
  administrative_area?: string | null;
  postal_code?: string | null;
}

export interface APIErrorDetail {
  field?: string | null;
  message: string;
  code: string;
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

export interface PaginationMeta {
  page: number;
  page_size: number;
  total_items: number;
  total_pages: number;
  has_next: boolean;
  has_previous: boolean;
}

export interface PaginatedResponse<T> {
  data: T[];
  pagination: PaginationMeta;
  meta: RequestMetadata;
}
