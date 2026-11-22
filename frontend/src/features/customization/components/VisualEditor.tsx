"use client";

import React, { useState } from "react";
import { Smartphone, Tablet, Monitor, Undo2, Redo2, Layers, SlidersHorizontal, Save, Check } from "lucide-react";
import type { MenuCustomizationDocument, ComponentInstance } from "@/lib/customization/types";
import { EditorHistory } from "@/lib/customization/history";

interface VisualEditorProps {
  customization: MenuCustomizationDocument;
  onSave: (doc: MenuCustomizationDocument) => Promise<void>;
}

export function VisualEditor({ customization, onSave }: VisualEditorProps) {
  const [history] = useState(() => new EditorHistory<MenuCustomizationDocument>(customization));
  const [currentDoc, setCurrentDoc] = useState<MenuCustomizationDocument>(customization);
  const [selectedInstanceId, setSelectedInstanceId] = useState<string | null>(
    customization.components[0]?.instance_id || null
  );
  const [viewport, setViewport] = useState<"mobile" | "tablet" | "desktop">("mobile");
  const [isSaving, setIsSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);

  const selectedComponent = currentDoc.components.find((c) => c.instance_id === selectedInstanceId);

  const updateDoc = (newDoc: MenuCustomizationDocument) => {
    history.execute(newDoc);
    setCurrentDoc(newDoc);
    setSaveSuccess(false);
  };

  const handleUndo = () => {
    const prev = history.undo();
    if (prev) {
      setCurrentDoc(prev);
      setSaveSuccess(false);
    }
  };

  const handleRedo = () => {
    const next = history.redo();
    if (next) {
      setCurrentDoc(next);
      setSaveSuccess(false);
    }
  };

  const handlePropChange = (propKey: string, val: any) => {
    if (!selectedInstanceId) return;
    const newComponents = currentDoc.components.map((c) => {
      if (c.instance_id === selectedInstanceId) {
        return {
          ...c,
          props: {
            ...c.props,
            [propKey]: val,
          },
        };
      }
      return c;
    });
    updateDoc({
      ...currentDoc,
      components: newComponents,
    });
  };

  const handleSave = async () => {
    setIsSaving(true);
    try {
      await onSave(currentDoc);
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 3000);
    } finally {
      setIsSaving(false);
    }
  };

  const viewportWidths = {
    mobile: "max-w-[375px]",
    tablet: "max-w-[768px]",
    desktop: "max-w-[1024px]",
  };

  return (
    <div className="flex flex-col h-[700px] border border-zinc-200 rounded-xl bg-zinc-50 overflow-hidden">
      {/* Top Controls Bar */}
      <div className="flex items-center justify-between px-4 py-2.5 bg-white border-b border-zinc-200">
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={handleUndo}
            disabled={!history.canUndo()}
            title="Undo"
            className="p-1.5 rounded hover:bg-zinc-100 disabled:opacity-40 disabled:cursor-not-allowed text-zinc-600"
          >
            <Undo2 className="w-4 h-4" />
          </button>
          <button
            type="button"
            onClick={handleRedo}
            disabled={!history.canRedo()}
            title="Redo"
            className="p-1.5 rounded hover:bg-zinc-100 disabled:opacity-40 disabled:cursor-not-allowed text-zinc-600"
          >
            <Redo2 className="w-4 h-4" />
          </button>
          <span className="text-xs text-zinc-400">|</span>
          <span className="text-xs font-mono text-zinc-500">
            Rev #{currentDoc.metadata?.revision || 1}
          </span>
        </div>

        {/* Viewport switch */}
        <div className="flex items-center gap-1 bg-zinc-100 p-0.5 rounded-lg">
          <button
            type="button"
            onClick={() => setViewport("mobile")}
            className={`p-1.5 rounded-md text-xs font-medium transition-all ${
              viewport === "mobile" ? "bg-white text-zinc-900 shadow-sm" : "text-zinc-500 hover:text-zinc-700"
            }`}
          >
            <Smartphone className="w-4 h-4" />
          </button>
          <button
            type="button"
            onClick={() => setViewport("tablet")}
            className={`p-1.5 rounded-md text-xs font-medium transition-all ${
              viewport === "tablet" ? "bg-white text-zinc-900 shadow-sm" : "text-zinc-500 hover:text-zinc-700"
            }`}
          >
            <Tablet className="w-4 h-4" />
          </button>
          <button
            type="button"
            onClick={() => setViewport("desktop")}
            className={`p-1.5 rounded-md text-xs font-medium transition-all ${
              viewport === "desktop" ? "bg-white text-zinc-900 shadow-sm" : "text-zinc-500 hover:text-zinc-700"
            }`}
          >
            <Monitor className="w-4 h-4" />
          </button>
        </div>

        {/* Save button */}
        <button
          type="button"
          onClick={handleSave}
          disabled={isSaving}
          className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors shadow-sm disabled:opacity-50"
        >
          {saveSuccess ? (
            <>
              <Check className="w-3.5 h-3.5 text-emerald-300" />
              Saved
            </>
          ) : (
            <>
              <Save className="w-3.5 h-3.5" />
              {isSaving ? "Saving..." : "Save Draft"}
            </>
          )}
        </button>
      </div>

      {/* Main Workspace (3-Panels: Tree, Canvas, Inspector) */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left: Component Tree */}
        <div className="w-56 bg-white border-r border-zinc-200 p-3 overflow-y-auto">
          <div className="flex items-center gap-1.5 mb-2 text-xs font-semibold text-zinc-700">
            <Layers className="w-3.5 h-3.5 text-zinc-500" />
            Component Tree
          </div>
          <div className="space-y-1">
            {currentDoc.components.map((c) => (
              <button
                key={c.instance_id}
                type="button"
                onClick={() => setSelectedInstanceId(c.instance_id)}
                className={`w-full text-left px-2.5 py-1.5 rounded text-xs transition-colors flex items-center justify-between ${
                  selectedInstanceId === c.instance_id
                    ? "bg-blue-50 text-blue-700 font-medium border border-blue-200"
                    : "text-zinc-600 hover:bg-zinc-50"
                }`}
              >
                <span className="truncate capitalize">{c.component_id.replace(/-/g, " ")}</span>
                <span className="text-[10px] text-zinc-400 ml-1">#{c.position}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Center: Preview Canvas */}
        <div className="flex-1 bg-zinc-100/70 p-4 flex items-center justify-center overflow-auto">
          <div
            className={`w-full ${viewportWidths[viewport]} bg-white rounded-lg shadow-md border border-zinc-200 p-4 min-h-[480px] transition-all`}
          >
            <div className="text-[11px] font-mono text-zinc-400 mb-2 text-center border-b pb-1">
              {viewport.toUpperCase()} VIEWPORT · {currentDoc.theme.id} · {currentDoc.layout.id}
            </div>

            <div className="space-y-3">
              {currentDoc.components
                .filter((c) => c.visible !== false)
                .sort((a, b) => a.position - b.position)
                .map((comp) => (
                  <div
                    key={comp.instance_id}
                    onClick={() => setSelectedInstanceId(comp.instance_id)}
                    className={`p-2.5 rounded border transition-all cursor-pointer ${
                      selectedInstanceId === comp.instance_id
                        ? "border-blue-500 ring-2 ring-blue-100 bg-blue-50/20"
                        : "border-dashed border-zinc-200 hover:border-zinc-300"
                    }`}
                  >
                    <div className="text-[11px] font-medium text-zinc-700 capitalize flex items-center justify-between">
                      <span>{comp.component_id.replace(/-/g, " ")}</span>
                      <span className="text-[9px] text-zinc-400">{comp.slot}</span>
                    </div>
                  </div>
                ))}
            </div>
          </div>
        </div>

        {/* Right: Property Inspector */}
        <div className="w-64 bg-white border-l border-zinc-200 p-3 overflow-y-auto">
          <div className="flex items-center gap-1.5 mb-2 text-xs font-semibold text-zinc-700">
            <SlidersHorizontal className="w-3.5 h-3.5 text-zinc-500" />
            Property Inspector
          </div>

          {selectedComponent ? (
            <div className="space-y-3">
              <div>
                <label className="text-[11px] text-zinc-400 block mb-1">Instance ID</label>
                <input
                  type="text"
                  disabled
                  value={selectedComponent.instance_id}
                  className="w-full text-xs font-mono bg-zinc-50 border border-zinc-200 rounded px-2 py-1 text-zinc-500"
                />
              </div>

              <div>
                <label className="text-[11px] text-zinc-400 block mb-1">Slot Position</label>
                <div className="text-xs text-zinc-700 font-mono">
                  {selectedComponent.slot} (pos: {selectedComponent.position})
                </div>
              </div>

              {/* Dynamic Props */}
              <div className="border-t border-zinc-100 pt-2 space-y-2">
                <div className="text-xs font-medium text-zinc-800">Properties</div>
                {Object.entries(selectedComponent.props || {}).map(([key, val]) => (
                  <div key={key}>
                    <label className="text-[11px] text-zinc-600 block mb-0.5 capitalize">
                      {key.replace(/_/g, " ")}
                    </label>
                    {typeof val === "boolean" ? (
                      <input
                        type="checkbox"
                        checked={val}
                        onChange={(e) => handlePropChange(key, e.target.checked)}
                        className="w-4 h-4 text-blue-600 rounded border-zinc-300 cursor-pointer"
                      />
                    ) : (
                      <input
                        type="text"
                        value={String(val)}
                        onChange={(e) => handlePropChange(key, e.target.value)}
                        className="w-full text-xs border border-zinc-200 rounded px-2 py-1 text-zinc-800"
                      />
                    )}
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="text-xs text-zinc-400 text-center py-8">Select a component to inspect</div>
          )}
        </div>
      </div>
    </div>
  );
}
