import type {
  OperationalSettingsDTO,
  RestaurantBrandingDTO,
  RestaurantProfileConfigDTO,
  RestaurantPublicationDTO,
  ServiceModeDTO,
  WeeklyHourRowDTO,
} from '@menu-it/shared-types';
import { apiRequest } from './api-client';

export const restaurantConfigApi = {
  getProfile: (restaurantId: string) =>
    apiRequest<RestaurantProfileConfigDTO>(`/api/v1/restaurants/${restaurantId}/profile`),

  updateProfile: (
    restaurantId: string,
    payload: Partial<
      Omit<RestaurantProfileConfigDTO, 'id' | 'organization_id' | 'restaurant_id' | 'version'>
    > & {
      expected_version?: number;
    },
  ) =>
    apiRequest<RestaurantProfileConfigDTO>(`/api/v1/restaurants/${restaurantId}/profile`, {
      method: 'PATCH',
      body: JSON.stringify(payload),
    }),

  getBranding: (restaurantId: string) =>
    apiRequest<RestaurantBrandingDTO>(`/api/v1/restaurants/${restaurantId}/branding`),

  updateBranding: (
    restaurantId: string,
    payload: Partial<
      Omit<RestaurantBrandingDTO, 'id' | 'organization_id' | 'restaurant_id' | 'revision'>
    > & {
      expected_revision?: number;
    },
  ) =>
    apiRequest<RestaurantBrandingDTO>(`/api/v1/restaurants/${restaurantId}/branding`, {
      method: 'PUT',
      body: JSON.stringify(payload),
    }),

  getHours: (restaurantId: string) =>
    apiRequest<WeeklyHourRowDTO[]>(`/api/v1/restaurants/${restaurantId}/hours`),

  replaceHours: (
    restaurantId: string,
    days: Array<{
      day_of_week: number;
      is_closed: boolean;
      intervals: Array<{ opens_at: string; closes_at: string; closes_next_day?: boolean }>;
    }>,
  ) =>
    apiRequest<WeeklyHourRowDTO[]>(`/api/v1/restaurants/${restaurantId}/hours`, {
      method: 'PUT',
      body: JSON.stringify({ days }),
    }),

  getServices: (restaurantId: string) =>
    apiRequest<ServiceModeDTO[]>(`/api/v1/restaurants/${restaurantId}/services`),

  updateServices: (
    restaurantId: string,
    modes: Array<{
      service_type: string;
      enabled: boolean;
      requires_customer_address?: boolean;
      accepts_scheduled_orders?: boolean;
      minimum_notice_minutes?: number;
    }>,
  ) =>
    apiRequest<ServiceModeDTO[]>(`/api/v1/restaurants/${restaurantId}/services`, {
      method: 'PUT',
      body: JSON.stringify({ modes }),
    }),

  getOperations: (restaurantId: string) =>
    apiRequest<OperationalSettingsDTO>(`/api/v1/restaurants/${restaurantId}/operations`),

  updateOperations: (
    restaurantId: string,
    payload: Omit<OperationalSettingsDTO, 'id' | 'revision'>,
  ) =>
    apiRequest<OperationalSettingsDTO>(`/api/v1/restaurants/${restaurantId}/operations`, {
      method: 'PUT',
      body: JSON.stringify(payload),
    }),

  publishProfile: (
    restaurantId: string,
    payload: { public_slug?: string; change_summary?: string } = {},
  ) =>
    apiRequest<RestaurantPublicationDTO>(`/api/v1/restaurants/${restaurantId}/publish`, {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  unpublishProfile: (restaurantId: string) =>
    apiRequest<RestaurantPublicationDTO>(`/api/v1/restaurants/${restaurantId}/unpublish`, {
      method: 'POST',
    }),
};
