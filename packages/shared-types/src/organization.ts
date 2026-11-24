/**
 * Organization domain types and API contracts (FCD-06 §13).
 */

import type { UUID } from './common.js';

export type OrganizationLifecycleStatus = 'active' | 'suspended' | 'archived';

export interface OrganizationReferenceDTO {
  id: UUID;
  name: string;
  slug: string;
  status: OrganizationLifecycleStatus;
}
