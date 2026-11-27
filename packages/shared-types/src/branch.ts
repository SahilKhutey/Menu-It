/**
 * Branch and Branch Assignment API contracts (FCD-14).
 */

import type { ISO8601String, UUID } from './common.js';

export type BranchLifecycleStatus = 'active' | 'inactive' | 'suspended' | 'archived';
export type BranchRole = 'branch_manager' | 'branch_staff';

export interface BranchDTO {
  id: UUID;
  organization_id: UUID;
  restaurant_id: UUID;
  name: string;
  slug: string;
  branch_code?: string | null;
  email?: string | null;
  phone?: string | null;
  address_line_1?: string | null;
  address_line_2?: string | null;
  city?: string | null;
  state_region?: string | null;
  postal_code?: string | null;
  country_code: string;
  timezone: string;
  status: BranchLifecycleStatus;
  created_at: ISO8601String;
  updated_at: ISO8601String;
}

export interface BranchCreateRequest {
  name: string;
  slug: string;
  timezone: string;
  country_code: string;
  branch_code?: string | null;
  email?: string | null;
  phone?: string | null;
  address_line_1?: string | null;
  city?: string | null;
  state_region?: string | null;
  postal_code?: string | null;
}

export interface BranchAssignmentDTO {
  id: UUID;
  organization_id: UUID;
  restaurant_id: UUID;
  branch_id: UUID;
  user_id: UUID;
  role: BranchRole;
  status: string;
  created_at: ISO8601String;
  updated_at: ISO8601String;
}
