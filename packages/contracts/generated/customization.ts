/**
 * ModularMenu — Canonical Menu Customization Document (ARC-08 §9).
 * Generated from menu-customization.schema.json.
 */
import type { ThemeSelection } from "./themes";
import type { LayoutSelection } from "./layouts";
import type { ComponentInstance } from "./components";

export type CustomizationMetadata = {
  revision: number;
  updated_at: string | null;
};

export type MenuCustomizationDocument = {
  configuration_version: "1.0.0";
  schema_version: "1.0.0";
  theme: ThemeSelection;
  layout: LayoutSelection;
  components: ComponentInstance[];
  metadata?: CustomizationMetadata;
};

export type ResolvedTheme = {
  themeId: string;
  themeVersion: string;
  tokens: Record<string, unknown>;
};

export type ResolvedCustomization = {
  configurationVersion: "1.0.0";
  theme: ResolvedTheme;
  layout: {
    id: string;
    version: string;
    settings: Record<string, unknown>;
    responsive: Record<string, unknown>;
  };
  components: ComponentInstance[];
};
