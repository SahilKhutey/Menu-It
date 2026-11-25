/**
 * TypeScript contracts for asynchronous background jobs and DLQ (FCD-10 WP-03, WP-04).
 */

export type JobStatus =
  'queued' | 'running' | 'succeeded' | 'retry_scheduled' | 'dead_lettered' | 'cancelled';

export interface JobContext {
  organizationId?: string | null;
  actorUserId?: string | null;
  correlationId: string;
  initiatedBy: 'user' | 'system' | 'scheduler';
}

export interface JobEnvelope<T = Record<string, unknown>> {
  jobId: string;
  jobType: string;
  schemaVersion: number;
  payload: T;
  context: JobContext;
  createdAt: string;
  idempotencyKey: string;
}

export interface JobResponseData {
  job_id: string;
  job_type: string;
  status: JobStatus;
  created_at: string;
}

export interface DeadLetterResponseData {
  id: string;
  job_id: string;
  job_type: string;
  failure_code: string;
  failure_message: string;
  attempts: number;
  dead_lettered_at: string;
  correlation_id: string;
  replayed_at?: string | null;
}
