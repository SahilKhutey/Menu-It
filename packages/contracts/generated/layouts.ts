/**
 * ModularMenu — Layout Definition Contract (ARC-08 §7).
 * Generated from layout-definition.schema.json.
 */

export type LayoutSettings = {
  content_width?: "compact" | "normal" | "wide" | "full";
  category_navigation?: "sticky" | "inline" | "tabs" | "sidebar";
  item_density?: "compact" | "comfortable" | "spacious";
  image_ratio?: "1:1" | "4:3" | "16:9" | "hidden";
};

export type ResponsiveProfile = {
  columns: number;
  navigation?: string;
};

export type LayoutResponsiveSettings = {
  mobile: ResponsiveProfile;
  tablet: ResponsiveProfile;
  desktop: ResponsiveProfile;
};

export type LayoutDefinition = {
  id: string;
  name: string;
  version: string;
  schema_version: "1.0.0";
  description: string;
  supported_slots: string[];
  allowed_components: string[];
  default_settings: LayoutSettings;
  responsive: LayoutResponsiveSettings;
};

export type LayoutSelection = {
  id: string;
  version: string;
  settings: LayoutSettings;
  responsive: LayoutResponsiveSettings;
};
