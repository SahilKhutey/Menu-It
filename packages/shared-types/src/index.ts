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
