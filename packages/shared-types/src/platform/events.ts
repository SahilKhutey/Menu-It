/**
 * TypeScript contracts for event envelopes and outbox (FCD-10 WP-05).
 */

export interface EventEnvelope<T = Record<string, unknown>> {
  eventId: string;
  eventType: string;
  schemaVersion: number;
  occurredAt: string;
  organizationId?: string | null;
  actorUserId?: string | null;
  correlationId: string;
  payload: T;
}
