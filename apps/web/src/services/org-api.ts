import type {
  BranchCreateRequest,
  BranchDTO,
  CreateRestaurantRequest,
  OrganizationCreateRequest,
  OrganizationDTO,
  OrganizationInvitationDTO,
  OrganizationMemberDTO,
  PaginatedData,
  RestaurantSummary,
} from '@menu-it/shared-types';
import { apiRequest } from './api-client';

export async function createOrganization(payload: OrganizationCreateRequest, token?: string) {
  return apiRequest<OrganizationDTO>('/organizations', {
    method: 'POST',
    body: JSON.stringify(payload),
    token,
  });
}

export async function listOrganizations(token?: string) {
  return apiRequest<OrganizationDTO[]>('/organizations', { token });
}

export async function getOrganization(organizationId: string, token?: string) {
  return apiRequest<OrganizationDTO>(`/organizations/${organizationId}`, { token });
}

export async function updateOrganization(
  organizationId: string,
  payload: Partial<OrganizationCreateRequest>,
  token?: string,
) {
  return apiRequest<OrganizationDTO>(`/organizations/${organizationId}`, {
    method: 'PATCH',
    body: JSON.stringify(payload),
    token,
  });
}

export async function listOrgRestaurants(organizationId: string, token?: string) {
  return apiRequest<PaginatedData<RestaurantSummary>>(
    `/organizations/${organizationId}/restaurants`,
    { token },
  );
}

export async function createOrgRestaurant(
  organizationId: string,
  payload: CreateRestaurantRequest,
  token?: string,
) {
  return apiRequest<RestaurantSummary>(`/organizations/${organizationId}/restaurants`, {
    method: 'POST',
    body: JSON.stringify(payload),
    token,
  });
}

export async function listRestaurantBranches(
  restaurantId: string,
  organizationId: string,
  token?: string,
) {
  return apiRequest<BranchDTO[]>(`/restaurants/${restaurantId}/branches`, {
    headers: { 'X-Organization-ID': organizationId },
    token,
  });
}

export async function createRestaurantBranch(
  restaurantId: string,
  organizationId: string,
  payload: BranchCreateRequest,
  token?: string,
) {
  return apiRequest<BranchDTO>(`/restaurants/${restaurantId}/branches`, {
    method: 'POST',
    headers: { 'X-Organization-ID': organizationId },
    body: JSON.stringify(payload),
    token,
  });
}

export async function listOrgMembers(organizationId: string, token?: string) {
  return apiRequest<OrganizationMemberDTO[]>(`/organizations/${organizationId}/members`, { token });
}

export async function listOrgInvitations(organizationId: string, token?: string) {
  return apiRequest<OrganizationInvitationDTO[]>(`/organizations/${organizationId}/invitations`, {
    token,
  });
}

export async function createOrgInvitation(
  organizationId: string,
  payload: { email: string; role: string },
  token?: string,
) {
  return apiRequest<OrganizationInvitationDTO & { invitation_token?: string }>(
    `/organizations/${organizationId}/invitations`,
    {
      method: 'POST',
      body: JSON.stringify(payload),
      token,
    },
  );
}
