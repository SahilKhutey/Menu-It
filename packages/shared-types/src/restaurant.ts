/**
 * Restaurant business profile, operating hours and API contracts (FCD-06 §13).
 */

import type { AddressDTO, ISO8601String, UUID } from './common.js';

export type RestaurantLifecycleStatus = 'active' | 'inactive' | 'suspended' | 'archived';

export interface OperatingHoursIntervalDTO {
  opens_at: string; // HH:MM
  closes_at: string; // HH:MM
}

export interface DailyOperatingHoursDTO {
  weekday: number; // 1-7 (Monday-Sunday)
  weekday_name: string;
  is_closed: boolean;
  time_ranges: OperatingHoursIntervalDTO[];
}

export type WeeklyOperatingScheduleDTO = DailyOperatingHoursDTO[];

export interface RestaurantProfileResponse {
  id: UUID;
  restaurant_id: UUID;
  organization_id: UUID;
  public_name: string;
  legal_name?: string | null;
  description?: string | null;
  email?: string | null;
  phone?: string | null;
  address?: AddressDTO | null;
  primary_currency: string;
  timezone: string;
  schedule?: WeeklyOperatingScheduleDTO | null;
  website_url?: string | null;
  logo_asset_id?: UUID | null;
  banner_asset_id?: UUID | null;
  version: number;
  created_at: ISO8601String;
  updated_at: ISO8601String;
}

export interface RestaurantProfileUpdateRequest {
  public_name?: string | null;
  legal_name?: string | null;
  description?: string | null;
  email?: string | null;
  phone?: string | null;
  address?: AddressDTO | null;
  primary_currency?: string | null;
  timezone?: string | null;
  schedule?: WeeklyOperatingScheduleDTO | null;
  website_url?: string | null;
  logo_asset_id?: UUID | null;
  banner_asset_id?: UUID | null;
}

export interface RestaurantSummary {
  id: UUID;
  organization_id: UUID;
  name: string;
  slug: string;
  timezone: string;
  status: RestaurantLifecycleStatus | string;
  created_at: ISO8601String;
  updated_at: ISO8601String;
}

export interface CreateRestaurantRequest {
  name: string;
  slug: string;
  timezone: string;
}
