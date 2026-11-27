export type ServiceType = 'DINE_IN' | 'TAKEAWAY' | 'PICKUP' | 'DELIVERY' | 'CURBSIDE_PICKUP';

export type PublicationStatus = 'draft' | 'ready' | 'published' | 'unpublished' | 'archived';

export interface RestaurantProfileConfigDTO {
  id: string;
  organization_id: string;
  restaurant_id: string;
  display_name: string;
  short_description?: string | null;
  description?: string | null;
  cuisine_type?: string | null;
  price_range?: string | null;
  website_url?: string | null;
  public_email?: string | null;
  public_phone?: string | null;
  social_links: Record<string, string>;
  version: number;
}

export interface RestaurantBrandingDTO {
  id: string;
  organization_id: string;
  restaurant_id: string;
  logo_asset_id?: string | null;
  alternate_logo_asset_id?: string | null;
  cover_asset_id?: string | null;
  favicon_asset_id?: string | null;
  primary_color?: string | null;
  secondary_color?: string | null;
  accent_color?: string | null;
  background_color?: string | null;
  text_color?: string | null;
  font_family?: string | null;
  border_radius?: string | null;
  theme_preset?: string | null;
  theme_settings: Record<string, unknown>;
  revision: number;
}

export interface WeeklyHourRowDTO {
  id: string;
  day_of_week: number;
  opens_at?: string | null;
  closes_at?: string | null;
  closes_next_day: boolean;
  is_closed: boolean;
}

export interface ServiceModeDTO {
  id: string;
  service_type: ServiceType;
  enabled: boolean;
  configuration: Record<string, unknown>;
}

export interface OperationalSettingsDTO {
  id: string;
  preparation_buffer_minutes: number;
  minimum_notice_minutes: number;
  maximum_advance_days: number;
  max_concurrent_orders?: number | null;
  auto_accept_orders: boolean;
  holiday_behavior: string;
  revision: number;
}

export interface RestaurantPublicationDTO {
  id: string;
  organization_id: string;
  restaurant_id: string;
  public_slug: string;
  status: PublicationStatus;
  published_revision?: number | null;
  published_at?: string | null;
}
