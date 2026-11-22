/**
 * ARC-10 Publishing Feature Types
 */
export type PublicationStatus = "READY" | "ACTIVE" | "SUPERSEDED" | "INACTIVE";

export type DiagnosticSeverity = "ERROR" | "WARNING" | "INFO";

export interface Diagnostic {
  code: string;
  path: string;
  message: string;
  severity: DiagnosticSeverity;
}

export interface ValidationReport {
  validation_id: string;
  menu_id: string;
  draft_revision: number;
  result: "PASSED" | "FAILED" | "WARNING";
  errors: Diagnostic[];
  warnings: Diagnostic[];
  validated_at: string;
}

export interface PublicationSummary {
  id: string;
  menu_id: string;
  restaurant_id: string;
  version_number: number;
  checksum: string;
  status: PublicationStatus;
  published_at: string;
  active_version_id?: string;
}

export interface PublishRequest {
  draft_revision: number;
  expected_active_publication_id?: string | null;
  reason?: string;
}

export interface PublishResponse {
  status: string;
  version_number: number;
  checksum: string;
  published_at: string;
  public_url: string;
  operation_id?: string;
  publication_id?: string;
  active_publication_id?: string;
}

export interface RollbackRequest {
  target_publication_id?: string;
  target_version_id?: string;
  expected_active_publication_id?: string | null;
  reason?: string;
}
