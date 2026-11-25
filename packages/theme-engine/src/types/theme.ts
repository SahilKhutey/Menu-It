/**
 * Theme Engine Types (FCD-08 WP-05).
 */

export type ThemeMode = 'light' | 'dark' | 'system';

export interface ThemeColors {
  background: string;
  foreground: string;
  surface: string;
  surfaceMuted: string;
  primary: string;
  primaryForeground: string;
  secondary: string;
  secondaryForeground: string;
  muted: string;
  mutedForeground: string;
  border: string;
  input: string;
  ring: string;
  accent: string;
  accentForeground: string;
  destructive: string;
  destructiveForeground: string;
  success: string;
  successForeground: string;
  warning: string;
  warningForeground: string;
  info: string;
  infoForeground: string;
}

export interface ThemeTypography {
  fontFamily: string;
  headingFontFamily?: string;
  baseFontSize: '14px' | '15px' | '16px' | '17px' | '18px';
}

export interface ThemeRadii {
  card: '0.25rem' | '0.5rem' | '0.75rem' | '1rem' | '1.5rem';
  button: '0.25rem' | '0.5rem' | '0.75rem' | '1rem' | '9999px';
  input: '0.25rem' | '0.5rem' | '0.75rem';
}

export interface ThemeDefinition {
  id: string;
  name: string;
  version: number;
  isRestaurantTheme?: boolean;
  colors: ThemeColors;
  typography: ThemeTypography;
  radii: ThemeRadii;
}

export interface ThemePreference {
  mode: ThemeMode;
}
