'use client';

import React, {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react';
import type { ThemeDefinition, ThemeMode } from '../types/theme';
import { applyTheme, clearCustomTheme } from '../resolvers/apply-theme';

export interface ThemeContextValue {
  mode: ThemeMode;
  resolvedMode: 'light' | 'dark';
  setMode: (mode: ThemeMode) => void;
  restaurantTheme?: ThemeDefinition | null;
  setRestaurantTheme: (theme: ThemeDefinition | null) => void;
}

const ThemeContext = createContext<ThemeContextValue | null>(null);

const STORAGE_KEY = 'menu-it-theme-mode';

function resolveSystemMode(): 'light' | 'dark' {
  if (typeof window === 'undefined') {
    return 'light';
  }
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}

export interface ThemeProviderProps {
  children: ReactNode;
  defaultMode?: ThemeMode;
  initialRestaurantTheme?: ThemeDefinition | null;
}

export function ThemeProvider({
  children,
  defaultMode = 'system',
  initialRestaurantTheme = null,
}: ThemeProviderProps) {
  const [mode, setModeState] = useState<ThemeMode>(defaultMode);
  const [resolvedMode, setResolvedMode] = useState<'light' | 'dark'>('light');
  const [restaurantTheme, setRestaurantThemeState] = useState<ThemeDefinition | null>(
    initialRestaurantTheme,
  );
  const [mounted, setMounted] = useState(false);

  // Read stored preference after hydration
  useEffect(() => {
    try {
      const stored = window.localStorage.getItem(STORAGE_KEY);
      if (stored === 'light' || stored === 'dark' || stored === 'system') {
        setModeState(stored);
      }
    } catch {
      // Ignore localStorage access restrictions
    }
    setResolvedMode(mode === 'system' ? resolveSystemMode() : mode);
    setMounted(true);
  }, []);

  // Sync resolved mode when mode changes
  useEffect(() => {
    const nextResolved = mode === 'system' ? resolveSystemMode() : mode;
    setResolvedMode(nextResolved);
  }, [mode]);

  // Apply data-theme attribute on root
  useEffect(() => {
    if (!mounted) return;
    const root = document.documentElement;
    root.dataset.theme = resolvedMode;
    root.style.colorScheme = resolvedMode;
  }, [resolvedMode, mounted]);

  // Listen to OS system preference changes
  useEffect(() => {
    if (!mounted || mode !== 'system') return;
    const media = window.matchMedia('(prefers-color-scheme: dark)');
    const onChange = () => {
      const current = media.matches ? 'dark' : 'light';
      setResolvedMode(current);
    };
    media.addEventListener('change', onChange);
    return () => media.removeEventListener('change', onChange);
  }, [mode, mounted]);

  // Handle restaurant theme changes
  useEffect(() => {
    if (!mounted) return;
    if (restaurantTheme) {
      applyTheme(restaurantTheme);
    } else {
      clearCustomTheme();
    }
  }, [restaurantTheme, mounted]);

  const setMode = (nextMode: ThemeMode) => {
    setModeState(nextMode);
    try {
      window.localStorage.setItem(STORAGE_KEY, nextMode);
    } catch {
      // Ignore storage errors
    }
  };

  const setRestaurantTheme = (nextTheme: ThemeDefinition | null) => {
    setRestaurantThemeState(nextTheme);
  };

  const contextValue = useMemo<ThemeContextValue>(
    () => ({
      mode,
      resolvedMode,
      setMode,
      restaurantTheme,
      setRestaurantTheme,
    }),
    [mode, resolvedMode, restaurantTheme],
  );

  return <ThemeContext.Provider value={contextValue}>{children}</ThemeContext.Provider>;
}

export function useTheme(): ThemeContextValue {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider.');
  }
  return context;
}
