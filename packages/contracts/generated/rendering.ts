/**
 * ModularMenu — Rendering Engine Type Definitions (ARC-09 §4, §5).
 * Generated from JSON Schemas.
 */

export type RenderMode = "published" | "preview";

export type ItemAvailability = "available" | "unavailable" | "sold_out";

export interface RenderAsset {
  asset_id?: string;
  url: string;
  alt?: string;
  width: number;
  height: number;
  is_primary?: boolean;
}

export interface RenderPrice {
  amount_minor: number;
  currency: string;
}

export interface RenderMenuItem {
  id: string;
  name: string;
  description?: string | null;
  price?: RenderPrice | null;
  availability: ItemAvailability;
  dietary_labels?: string[];
  allergen_labels?: string[];
  images?: RenderAsset[];
}

export interface RenderCategory {
  id: string;
  name: string;
  description?: string | null;
  sort_order?: number;
  items: RenderMenuItem[];
}

export interface RenderRestaurant {
  name: string;
  slug: string;
  description?: string | null;
  logo?: RenderAsset | null;
  cover_image?: RenderAsset | null;
  contact_information?: Record<string, any> | null;
}

export interface RenderMenuData {
  id?: string;
  title: string;
  description?: string | null;
  status?: string;
  categories: RenderCategory[];
}

export interface MenuRenderInput {
  metadata: {
    render_mode: RenderMode;
    schema_version: string;
    locale: string;
    currency: string;
    snapshot_id?: string;
    menu_id?: string;
  };
  restaurant: RenderRestaurant;
  menu: RenderMenuData;
  resolved_configuration: {
    theme: {
      id: string;
      version: string;
      tokens: Record<string, any>;
    };
    layout: {
      id: string;
      version: string;
      settings?: Record<string, any>;
      responsive: Record<string, any>;
    };
    components: Array<{
      instance_id: string;
      component_id: string;
      component_version: string;
      slot: string;
      position: number;
      visible: boolean;
      props: Record<string, any>;
    }>;
    css_variables?: Record<string, string>;
  };
  media_manifest?: {
    approved_assets: Array<{
      asset_id?: string;
      url: string;
      mime_type?: string;
      width?: number;
      height?: number;
    }>;
  };
  publication?: {
    version: number;
    published_at: string;
    content_hash: string;
  } | null;
}

export interface RenderNode {
  id: string;
  componentId: string;
  componentVersion: string;
  slot: string;
  order: number;
  props: Record<string, any>;
  children: RenderNode[];
}

export interface MenuRenderPlan {
  schemaVersion: string;
  theme: {
    id: string;
    version: string;
    tokens: Record<string, any>;
  };
  layout: {
    id: string;
    version: string;
    slots: string[];
  };
  root: RenderNode[];
  warnings: Array<{
    code: string;
    message: string;
  }>;
}

export interface RenderErrorDetail {
  code: string;
  message: string;
  stage: string;
  details?: any;
}
