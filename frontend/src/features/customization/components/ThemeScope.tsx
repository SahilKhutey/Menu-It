import React from "react";
import { toCssVariables } from "@/lib/customization/css-variables";

interface ThemeScopeProps {
  tokens: Record<string, any>;
  children: React.ReactNode;
  className?: string;
}

export function ThemeScope({ tokens, children, className = "" }: ThemeScopeProps) {
  const cssVars = toCssVariables(tokens);
  return (
    <div
      style={cssVars as React.CSSProperties}
      data-theme-scope="modularmenu"
      className={`theme-scope-container transition-colors duration-200 ${className}`}
    >
      {children}
    </div>
  );
}
