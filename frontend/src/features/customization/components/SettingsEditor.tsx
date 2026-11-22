"use client";

import React from "react";
import type { MenuCustomizationDocument } from "@/lib/customization/types";

interface SettingsEditorProps {
  customization: MenuCustomizationDocument;
  onChange: (updated: MenuCustomizationDocument) => void;
  themes: Array<{ id: string; name: string; description: string }>;
  layouts: Array<{ id: string; name: string; description: string }>;
}

export function SettingsEditor({
  customization,
  onChange,
  themes,
  layouts,
}: SettingsEditorProps) {
  const currentThemeId = customization.theme?.id || "theme-minimal";
  const currentLayoutId = customization.layout?.id || "layout-grid";
  const overrides = customization.theme?.overrides || {};
  const brandPrimary = (overrides as any)?.color?.brand?.primary || "#18181B";

  const handleThemeChange = (newThemeId: string) => {
    onChange({
      ...customization,
      theme: {
        ...customization.theme,
        id: newThemeId,
        version: "1.0.0",
      },
    });
  };

  const handleLayoutChange = (newLayoutId: string) => {
    onChange({
      ...customization,
      layout: {
        ...customization.layout,
        id: newLayoutId,
        version: "1.0.0",
      },
    });
  };

  const handlePrimaryColorChange = (hex: string) => {
    const newOverrides = {
      ...overrides,
      color: {
        ...(overrides as any)?.color,
        brand: {
          ...(overrides as any)?.color?.brand,
          primary: hex,
        },
      },
    };
    onChange({
      ...customization,
      theme: {
        ...customization.theme,
        overrides: newOverrides,
      },
    });
  };

  const handleToggleComponent = (instanceId: string) => {
    const updatedComponents = customization.components.map((c) =>
      c.instance_id === instanceId ? { ...c, visible: !c.visible } : c
    );
    onChange({
      ...customization,
      components: updatedComponents,
    });
  };

  return (
    <div className="space-y-6 text-sm text-zinc-800">
      {/* Theme Presets */}
      <div>
        <h3 className="font-semibold text-zinc-900 mb-2">Theme Preset</h3>
        <div className="grid grid-cols-2 gap-2">
          {themes.map((t) => (
            <button
              key={t.id}
              type="button"
              onClick={() => handleThemeChange(t.id)}
              className={`p-3 text-left rounded-lg border transition-all ${
                currentThemeId === t.id
                  ? "border-blue-600 bg-blue-50/50 shadow-sm"
                  : "border-zinc-200 hover:border-zinc-300 bg-white"
              }`}
            >
              <div className="font-medium text-xs text-zinc-900">{t.name}</div>
              <div className="text-[11px] text-zinc-500 line-clamp-1">{t.description}</div>
            </button>
          ))}
        </div>
      </div>

      {/* Layout Selection */}
      <div>
        <h3 className="font-semibold text-zinc-900 mb-2">Layout Structure</h3>
        <div className="grid grid-cols-2 gap-2">
          {layouts.map((l) => (
            <button
              key={l.id}
              type="button"
              onClick={() => handleLayoutChange(l.id)}
              className={`p-3 text-left rounded-lg border transition-all ${
                currentLayoutId === l.id
                  ? "border-blue-600 bg-blue-50/50 shadow-sm"
                  : "border-zinc-200 hover:border-zinc-300 bg-white"
              }`}
            >
              <div className="font-medium text-xs text-zinc-900">{l.name}</div>
              <div className="text-[11px] text-zinc-500 line-clamp-1">{l.description}</div>
            </button>
          ))}
        </div>
      </div>

      {/* Color Overrides */}
      <div>
        <h3 className="font-semibold text-zinc-900 mb-2">Brand Color Accent</h3>
        <div className="flex items-center gap-3">
          <input
            type="color"
            value={brandPrimary}
            onChange={(e) => handlePrimaryColorChange(e.target.value)}
            className="w-9 h-9 p-0.5 rounded border border-zinc-300 cursor-pointer"
          />
          <span className="font-mono text-xs text-zinc-600">{brandPrimary}</span>
        </div>
      </div>

      {/* Component Visibility Toggles */}
      <div>
        <h3 className="font-semibold text-zinc-900 mb-2">Component Visibility</h3>
        <div className="space-y-2">
          {customization.components.map((c) => (
            <label
              key={c.instance_id}
              className="flex items-center justify-between p-2 rounded bg-zinc-50 border border-zinc-100 cursor-pointer hover:bg-zinc-100/60 transition-colors"
            >
              <span className="text-xs font-medium text-zinc-700 capitalize">
                {c.component_id.replace(/-/g, " ")}
              </span>
              <input
                type="checkbox"
                checked={c.visible !== false}
                onChange={() => handleToggleComponent(c.instance_id)}
                className="w-4 h-4 text-blue-600 rounded border-zinc-300 focus:ring-blue-500 cursor-pointer"
              />
            </label>
          ))}
        </div>
      </div>
    </div>
  );
}
