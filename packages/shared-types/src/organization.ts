/**
 * Organization, Membership, and Invitation domain types and API contracts (FCD-06 §13, FCD-14).
 */

import type { ISO8601String, UUID } from './common.js';

export type OrganizationLifecycleStatus =
  'provisioning' | 'active' | 'suspended' | 'offboarding' | 'deactivated' | 'archived';

export type OrganizationRole = 'owner' | 'admin' | 'manager' | 'staff' | 'viewer';
export type MembershipStatus = 'invited' | 'active' | 'suspended' | 'revoked';
export type InvitationStatus = 'pending' | 'accepted' | 'revoked' | 'expired';

export interface OrganizationReferenceDTO {
  id: UUID;
  name: string;
  slug: string;
  status: OrganizationLifecycleStatus;
}

export interface OrganizationDTO {
  id: UUID;
  name: string;
  slug: string;
  legal_name?: string | null;
  organization_type: string;
  email?: string | null;
  phone?: string | null;
  website?: string | null;
  country_code: string;
  currency_code: string;
  timezone: string;
  status: OrganizationLifecycleStatus;
  created_at: ISO8601String;
  updated_at: ISO8601String;
}

export interface OrganizationCreateRequest {
  name: string;
  slug: string;
  currency_code: string;
  timezone: string;
  country_code: string;
  legal_name?: string | null;
  email?: string | null;
  phone?: string | null;
  website?: string | null;
}

export interface OrganizationMemberDTO {
  id: UUID;
  organization_id: UUID;
  user_id: UUID;
  role: OrganizationRole;
  status: MembershipStatus;
  joined_at?: ISO8601String | null;
  created_at: ISO8601String;
  updated_at: ISO8601String;
}

export interface OrganizationInvitationDTO {
  id: UUID;
  organization_id: UUID;
  email: string;
  role: OrganizationRole;
  status: InvitationStatus;
  expires_at: ISO8601String;
  created_at: ISO8601String;
}
