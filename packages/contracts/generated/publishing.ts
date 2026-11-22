/**
 * ARC-10 Publishing & Versioning TypeScript Contracts
 * Generated from JSON Schemas and Architecture Specifications
 */

export type PublicationStatus = "READY" | "ACTIVE" | "SUPERSEDED" | "INACTIVE";

export type OperationType = "publish" | "rollback" | "schedule" | "reconcile";

export type OperationStatus =
  | "REQUESTED"
  | "VALIDATING"
  | "PREPARING"
  | "PREPARED"
  | "ACTIVATING"
  | "COMPLETED"
  | "FAILED"
  | "REJECTED";

export type DiagnosticSeverity = "ERROR" | "WARNING" | "INFO";

export interface Diagnostic {
  code: string;
  path: string;
  message: string;
  severity: DiagnosticSeverity;
}

export interface DraftRevisionContract {
  id: string;
  organization_id: string;
  menu_id: string;
  revision_number: number;
  content_hash: string;
  parent_revision_id: string | null;
  created_by: string;
  created_at: string;
  payload: Record<string, any>;
}

export interface PublicationValidationContract {
  validation_id: string;
  menu_id: string;
  draft_revision: number;
  result: "PASSED" | "FAILED" | "WARNING";
  errors: Diagnostic[];
  warnings: Diagnostic[];
  validated_at: string;
}

export interface PublicationSummaryContract {
  id: string;
  version_number: number;
  snapshot_id: string;
  status: PublicationStatus;
  created_at: string;
  activated_at: string | null;
  checksum?: string;
}

export interface PublicationResponseContract {
  operation_id: string;
  publication: PublicationSummaryContract;
  active_publication_id: string;
}

export interface RollbackRequestContract {
  target_publication_id: string;
  expected_active_publication_id?: string | null;
  reason?: string;
}

export interface PublicationActivationContract {
  id: string;
  organization_id: string;
  menu_id: string;
  publication_id: string;
  previous_publication_id: string | null;
  operation_id: string;
  activation_reason: "publish" | "rollback" | "scheduled" | "recovery";
  actor_id: string | null;
  activated_at: string;
}

export interface PublicationOperationContract {
  id: string;
  organization_id: string;
  menu_id: string;
  actor_id: string;
  operation_type: OperationType;
  idempotency_key: string;
  request_hash: string;
  status: OperationStatus;
  result_publication_id: string | null;
  error_code: string | null;
  created_at: string;
  completed_at: string | null;
}

export interface ScheduledPublicationContract {
  id: string;
  organization_id: string;
  menu_id: string;
  draft_revision: number;
  expected_active_publication_id: string | null;
  scheduled_at: string;
  timezone_name: string;
  status: "SCHEDULED" | "EXECUTING" | "COMPLETED" | "CANCELLED" | "FAILED";
  created_by: string;
}
