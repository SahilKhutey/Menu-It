/**
 * ModularMenu — Design Tokens Contract (ARC-08 §5).
 * Generated from design-tokens.schema.json.
 */

export type ColorBrand = {
  primary: string;
  secondary?: string;
  accent?: string;
};

export type ColorSurface = {
  default: string;
  subtle?: string;
  raised?: string;
};

export type ColorText = {
  primary: string;
  secondary?: string;
  inverse?: string;
};

export type ColorBorder = {
  default: string;
  subtle?: string;
};

export type ColorStatus = {
  success?: string;
  warning?: string;
  error?: string;
};

export type ColorTokens = {
  brand: ColorBrand;
  surface: ColorSurface;
  text: ColorText;
  border: ColorBorder;
  status?: ColorStatus;
};

export type TypographyFontFamily = {
  body: "system" | "inter" | "cinzel" | "playfair" | "merriweather" | "roboto" | "lato" | string;
  heading: "system" | "inter" | "cinzel" | "playfair" | "merriweather" | "roboto" | "lato" | string;
};

export type TypographyFontSize = {
  small: string;
  body: string;
  heading: string;
  display: string;
};

export type TypographyFontWeight = {
  normal: number;
  medium: number;
  bold: number;
};

export type TypographyTokens = {
  fontFamily: TypographyFontFamily;
  fontSize: TypographyFontSize;
  fontWeight: TypographyFontWeight;
};

export type SpacingTokens = {
  xs: string;
  sm: string;
  md: string;
  lg: string;
  xl: string;
  "2xl"?: string;
};

export type RadiusTokens = {
  none?: string;
  small: string;
  medium: string;
  large: string;
  full?: string;
};

export type ShadowTokens = {
  none?: string;
  sm?: string;
  card: string;
  raised?: string;
  floating?: string;
};

export type MotionTokens = {
  durationFast?: string;
  durationNormal?: string;
  durationSlow?: string;
};

export type DesignTokensMap = {
  color: ColorTokens;
  typography: TypographyTokens;
  spacing: SpacingTokens;
  radius: RadiusTokens;
  shadow: ShadowTokens;
  motion?: MotionTokens;
};

export type DesignTokensDocument = {
  schema_version: "1.0.0";
  tokens: DesignTokensMap;
};
