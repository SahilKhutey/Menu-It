/**
 * TypeScript design token constants and types.
 */

export const primitives = {
  colors: {
    white: '#ffffff',
    black: '#000000',
    neutral: {
      50: '#fafafa',
      100: '#f5f5f5',
      200: '#e5e5e5',
      300: '#d4d4d4',
      400: '#a3a3a3',
      500: '#737373',
      600: '#525252',
      700: '#404040',
      800: '#262626',
      900: '#171717',
    },
    brand: {
      50: '#eff6ff',
      100: '#dbeafe',
      200: '#bfdbfe',
      300: '#93c5fd',
      400: '#60a5fa',
      500: '#3b82f6',
      600: '#2563eb',
      700: '#1d4ed8',
      800: '#1e40af',
      900: '#1e3a8a',
    },
    success: '#16a34a',
    warning: '#d97706',
    danger: '#dc2626',
    info: '#0284c7',
  },
} as const;

export const semanticLight = {
  background: '#ffffff',
  foreground: '#171717',
  surface: '#ffffff',
  surfaceMuted: '#f5f5f5',
  primary: '#2563eb',
  primaryForeground: '#ffffff',
  secondary: '#f5f5f5',
  secondaryForeground: '#262626',
  muted: '#f5f5f5',
  mutedForeground: '#525252',
  accent: '#eff6ff',
  accentForeground: '#1d4ed8',
  border: '#e5e5e5',
  input: '#d4d4d4',
  ring: '#2563eb',
  success: '#15803d',
  successForeground: '#ffffff',
  warning: '#b45309',
  warningForeground: '#ffffff',
  destructive: '#dc2626',
  destructiveForeground: '#ffffff',
  info: '#0369a1',
  infoForeground: '#ffffff',
} as const;

export const semanticDark = {
  background: '#171717',
  foreground: '#fafafa',
  surface: '#262626',
  surfaceMuted: '#303030',
  primary: '#60a5fa',
  primaryForeground: '#0f172a',
  secondary: '#303030',
  secondaryForeground: '#fafafa',
  muted: '#303030',
  mutedForeground: '#a3a3a3',
  accent: '#1e3a5f',
  accentForeground: '#bfdbfe',
  border: '#404040',
  input: '#525252',
  ring: '#60a5fa',
  success: '#4ade80',
  successForeground: '#052e16',
  warning: '#fbbf24',
  warningForeground: '#451a03',
  destructive: '#f87171',
  destructiveForeground: '#450a0a',
  info: '#38bdf8',
  infoForeground: '#082f49',
} as const;

export const breakpoints = {
  sm: '40rem',
  md: '48rem',
  lg: '64rem',
  xl: '80rem',
  '2xl': '96rem',
} as const;

export const spacing = {
  0: '0',
  1: '0.25rem',
  2: '0.5rem',
  3: '0.75rem',
  4: '1rem',
  5: '1.25rem',
  6: '1.5rem',
  8: '2rem',
  10: '2.5rem',
  12: '3rem',
  16: '4rem',
  20: '5rem',
} as const;

export const radii = {
  none: '0',
  sm: '0.25rem',
  md: '0.5rem',
  lg: '0.75rem',
  xl: '1rem',
  '2xl': '1.5rem',
  full: '9999px',
} as const;
