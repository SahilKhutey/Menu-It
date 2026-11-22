/**
 * ModularMenu — Theme Definition Contract (ARC-08 §6).
 * Generated from theme-definition.schema.json.
 */
import type { DesignTokensMap } from "./tokens";

export type ThemeStatus = "draft" | "published" | "deprecated" | "retired";

export type ThemeDefinition = {
  id: string;
  name: string;
  slug: string;
  description: string;
  version: string;
  schema_version: "1.0.0";
  status: ThemeStatus;
  tokens: DesignTokensMap;
  supported_layouts: string[];
  supported_components: string[];
  preview_thumbnail?: string;
};

export type ThemeSelection = {
  id: string;
  version: string;
  overrides: Partial<DesignTokensMap>;
};
