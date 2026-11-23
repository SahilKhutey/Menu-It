import React from "react";

export interface ThemeColors {
  surface: string;
  surfaceElevated: string;
  surfaceMuted: string;
  textPrimary: string;
  textMuted: string;
  primary: string;
  primaryForeground: string;
  accent: string;
  border: string;
  dietaryVeg: string;
  dietaryNonVeg: string;
  dietaryEgg: string;
}

export interface ThemeTypography {
  fontHeading: string;
  fontBody: string;
  fontPrice: string;
  baseSize: number;
  scaleRatio: number;
}

export interface ThemeLayout {
  borderRadius: "none" | "sm" | "md" | "lg" | "full";
  cardStyle: "flat" | "bordered" | "elevated" | "glass";
  itemSpacing: "compact" | "comfortable" | "spacious";
  imageAspectRatio: "square" | "video" | "portrait" | "none";
}

export interface ThemeConfig {
  name: string;
  theme_key: string;
  is_system_preset: boolean;
  tokens: {
    colors: ThemeColors;
    typography: ThemeTypography;
    layout: ThemeLayout;
  };
}

export const THEME_PRESETS: ThemeConfig[] = [
  {
    name: "Luxury",
    theme_key: "luxury",
    is_system_preset: true,
    tokens: {
      colors: {
        surface: "#0D0E12",
        surfaceElevated: "#16181F",
        surfaceMuted: "#222530",
        textPrimary: "#F8F9FA",
        textMuted: "#9CA3AF",
        primary: "#D4AF37",
        primaryForeground: "#0D0E12",
        accent: "#E5C365",
        border: "#2D3139",
        dietaryVeg: "#22C55E",
        dietaryNonVeg: "#EF4444",
        dietaryEgg: "#F59E0B",
      },
      typography: {
        fontHeading: "Cinzel, serif",
        fontBody: "Plus Jakarta Sans, sans-serif",
        fontPrice: "Cinzel, serif",
        baseSize: 16,
        scaleRatio: 1.25,
      },
      layout: {
        borderRadius: "sm",
        cardStyle: "elevated",
        itemSpacing: "comfortable",
        imageAspectRatio: "portrait",
      },
    },
  },
  {
    name: "Minimal",
    theme_key: "minimal",
    is_system_preset: true,
    tokens: {
      colors: {
        surface: "#FFFFFF",
        surfaceElevated: "#F4F4F5",
        surfaceMuted: "#E4E4E7",
        textPrimary: "#09090B",
        textMuted: "#71717A",
        primary: "#18181B",
        primaryForeground: "#FFFFFF",
        accent: "#71717A",
        border: "#E4E4E7",
        dietaryVeg: "#16A34A",
        dietaryNonVeg: "#DC2626",
        dietaryEgg: "#D97706",
      },
      typography: {
        fontHeading: "Inter, sans-serif",
        fontBody: "Inter, sans-serif",
        fontPrice: "Inter, sans-serif",
        baseSize: 16,
        scaleRatio: 1.2,
      },
      layout: {
        borderRadius: "none",
        cardStyle: "bordered",
        itemSpacing: "compact",
        imageAspectRatio: "square",
      },
    },
  },
  {
    name: "Rustic",
    theme_key: "rustic",
    is_system_preset: true,
    tokens: {
      colors: {
        surface: "#FBF9F5",
        surfaceElevated: "#FFFFFF",
        surfaceMuted: "#F0EBE1",
        textPrimary: "#292524",
        textMuted: "#78716C",
        primary: "#78350F",
        primaryForeground: "#FFFFFF",
        accent: "#B45309",
        border: "#E7E0D3",
        dietaryVeg: "#15803D",
        dietaryNonVeg: "#B91C1C",
        dietaryEgg: "#B45309",
      },
      typography: {
        fontHeading: "Merriweather, serif",
        fontBody: "Lora, serif",
        fontPrice: "Merriweather, serif",
        baseSize: 16,
        scaleRatio: 1.25,
      },
      layout: {
        borderRadius: "md",
        cardStyle: "elevated",
        itemSpacing: "comfortable",
        imageAspectRatio: "portrait",
      },
    },
  },
  {
    name: "Vibrant",
    theme_key: "vibrant",
    is_system_preset: true,
    tokens: {
      colors: {
        surface: "#FFFDF9",
        surfaceElevated: "#FFFFFF",
        surfaceMuted: "#FEF3C7",
        textPrimary: "#1E1B4B",
        textMuted: "#6B7280",
        primary: "#E11D48",
        primaryForeground: "#FFFFFF",
        accent: "#F59E0B",
        border: "#FDE68A",
        dietaryVeg: "#16A34A",
        dietaryNonVeg: "#E11D48",
        dietaryEgg: "#F59E0B",
      },
      typography: {
        fontHeading: "Outfit, sans-serif",
        fontBody: "Plus Jakarta Sans, sans-serif",
        fontPrice: "Outfit, sans-serif",
        baseSize: 16,
        scaleRatio: 1.25,
      },
      layout: {
        borderRadius: "lg",
        cardStyle: "elevated",
        itemSpacing: "spacious",
        imageAspectRatio: "video",
      },
    },
  },
  {
    name: "Contemporary",
    theme_key: "contemporary",
    is_system_preset: true,
    tokens: {
      colors: {
        surface: "#F8FAFC",
        surfaceElevated: "#FFFFFF",
        surfaceMuted: "#F1F5F9",
        textPrimary: "#0F172A",
        textMuted: "#64748B",
        primary: "#2563EB",
        primaryForeground: "#FFFFFF",
        accent: "#06B6D4",
        border: "#E2E8F0",
        dietaryVeg: "#16A34A",
        dietaryNonVeg: "#DC2626",
        dietaryEgg: "#D97706",
      },
      typography: {
        fontHeading: "Inter, sans-serif",
        fontBody: "Inter, sans-serif",
        fontPrice: "Inter, sans-serif",
        baseSize: 16,
        scaleRatio: 1.2,
      },
      layout: {
        borderRadius: "md",
        cardStyle: "bordered",
        itemSpacing: "comfortable",
        imageAspectRatio: "square",
      },
    },
  },
  {
    name: "Editorial",
    theme_key: "editorial",
    is_system_preset: true,
    tokens: {
      colors: {
        surface: "#FAFAFA",
        surfaceElevated: "#FFFFFF",
        surfaceMuted: "#F5F5F5",
        textPrimary: "#171717",
        textMuted: "#737373",
        primary: "#262626",
        primaryForeground: "#FFFFFF",
        accent: "#A3A3A3",
        border: "#E5E5E5",
        dietaryVeg: "#16A34A",
        dietaryNonVeg: "#DC2626",
        dietaryEgg: "#CA8A04",
      },
      typography: {
        fontHeading: "Playfair Display, serif",
        fontBody: "Source Serif 4, serif",
        fontPrice: "Playfair Display, serif",
        baseSize: 16,
        scaleRatio: 1.333,
      },
      layout: {
        borderRadius: "none",
        cardStyle: "flat",
        itemSpacing: "spacious",
        imageAspectRatio: "video",
      },
    },
  },
];

export function getRadiusValue(radius?: string): string {
  switch (radius) {
    case "none":
      return "0px";
    case "sm":
      return "0.25rem";
    case "md":
      return "0.5rem";
    case "lg":
      return "1rem";
    case "full":
      return "9999px";
    default:
      return "0.5rem";
  }
}

export function generateCssVariables(tokens: ThemeConfig["tokens"]): React.CSSProperties {
  const { colors, typography, layout } = tokens;
  return {
    "--theme-surface": colors.surface,
    "--theme-surface-elevated": colors.surfaceElevated,
    "--theme-surface-muted": colors.surfaceMuted,
    "--theme-text-primary": colors.textPrimary,
    "--theme-text-muted": colors.textMuted,
    "--theme-primary": colors.primary,
    "--theme-primary-foreground": colors.primaryForeground,
    "--theme-accent": colors.accent,
    "--theme-border": colors.border,
    "--theme-dietary-veg": colors.dietaryVeg,
    "--theme-dietary-nonveg": colors.dietaryNonVeg,
    "--theme-dietary-egg": colors.dietaryEgg,
    "--theme-font-heading": typography.fontHeading,
    "--theme-font-body": typography.fontBody,
    "--theme-font-price": typography.fontPrice,
    "--theme-radius": getRadiusValue(layout?.borderRadius),
  } as React.CSSProperties;
}
