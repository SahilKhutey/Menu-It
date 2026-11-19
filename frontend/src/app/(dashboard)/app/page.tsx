"use client";

import React, { useState } from "react";
import Link from "next/link";
import {
  Smartphone,
  Tablet,
  Monitor,
  Eye,
  RotateCcw,
  Sparkles,
  Layers,
  Palette,
  CheckCircle2,
  Share2,
  Plus,
  Flame,
  Leaf,
  Beef,
  Egg,
  Search,
  ExternalLink,
} from "lucide-react";
import { THEME_PRESETS, ThemeConfig, generateCssVariables } from "@/lib/themes";
import { formatPrice } from "@/lib/utils";

// Sample Initial Active Menu Data for The Bombay Canteen
interface DemoItem {
  id: string;
  name: string;
  description: string;
  price: number;
  dietary: "vegetarian" | "non_veg" | "egg";
  spice: "none" | "mild" | "medium" | "hot";
  isAvailable: boolean;
  isFeatured?: boolean;
}

interface DemoCategory {
  id: string;
  name: string;
  items: DemoItem[];
}

const INITIAL_CATEGORIES: DemoCategory[] = [
  {
    id: "cat-1",
    name: "Small Plates & Chintu",
    items: [
      {
        id: "item-1",
        name: "Barley & Jowar Salad",
        description: "Pomegranate seeds, spiced hung curd dressing, crispy sev, puffed amaranth.",
        price: 425,
        dietary: "vegetarian",
        spice: "mild",
        isAvailable: true,
        isFeatured: true,
      },
      {
        id: "item-2",
        name: "Chettinad Fried Chicken",
        description: "Curry leaf crisp, shallot chutney dip, buttermilk batter, crushed pepper.",
        price: 525,
        dietary: "non_veg",
        spice: "hot",
        isAvailable: true,
        isFeatured: true,
      },
      {
        id: "item-3",
        name: "Eggs Kejriwal Toast",
        description: "Sunny side up egg, toasted sourdough, melted white cheddar, green chilli tadka.",
        price: 450,
        dietary: "egg",
        spice: "medium",
        isAvailable: true,
      },
    ],
  },
  {
    id: "cat-2",
    name: "Big Plates & Curries",
    items: [
      {
        id: "item-4",
        name: "Paneer & Fig Kofta",
        description: "Almond yogurt gravy, fenugreek cream, served with flaky malabar parotta.",
        price: 650,
        dietary: "vegetarian",
        spice: "mild",
        isAvailable: true,
      },
      {
        id: "item-5",
        name: "Kerala Roast Duck",
        description: "Slow-roasted duck leg, tellicherry black pepper, shallots, coconut oil drizzle.",
        price: 895,
        dietary: "non_veg",
        spice: "hot",
        isAvailable: true,
      },
    ],
  },
  {
    id: "cat-3",
    name: "Breads & Rice",
    items: [
      {
        id: "item-6",
        name: "Truffle & Wild Mushroom Kulcha",
        description: "Smoked scamorza cheese, fresh coriander butter, black truffle glaze.",
        price: 375,
        dietary: "vegetarian",
        spice: "none",
        isAvailable: true,
        isFeatured: true,
      },
    ],
  },
];

export default function VisualStudioPage() {
  const [selectedTheme, setSelectedTheme] = useState<ThemeConfig>(THEME_PRESETS[0]); // Default Luxury
  const [activeViewport, setActiveViewport] = useState<"mobile" | "tablet" | "desktop">("mobile");
  const [categories, setCategories] = useState<DemoCategory[]>(INITIAL_CATEGORIES);
  const [selectedCategory, setSelectedCategory] = useState<string>("cat-1");
  const [isPublished, setIsPublished] = useState(false);
  const [publishVersion, setPublishVersion] = useState(1);
  const [activeFilter, setActiveFilter] = useState<string>("all");

  // Dynamic CSS variables applied to the live preview
  const livePreviewStyles = generateCssVariables(selectedTheme.tokens);

  const toggleAvailability = (catId: string, itemId: string) => {
    setCategories((prev) =>
      prev.map((cat) => {
        if (cat.id !== catId) return cat;
        return {
          ...cat,
          items: cat.items.map((it) => (it.id === itemId ? { ...it, isAvailable: !it.isAvailable } : it)),
        };
      })
    );
  };

  const handlePublish = () => {
    setIsPublished(true);
    setPublishVersion((v) => v + 1);
    setTimeout(() => {
      setIsPublished(false);
    }, 4000);
  };

  return (
    <div className="h-screen flex flex-col bg-slate-950 text-slate-100 overflow-hidden font-sans">
      {/* Top Navbar */}
      <header className="h-14 border-b border-slate-800 bg-slate-900/90 px-4 flex items-center justify-between shrink-0 z-30">
        <div className="flex items-center gap-3">
          <Link href="/" className="flex items-center gap-2 text-slate-400 hover:text-white transition-colors">
            <span className="font-bold text-amber-500">ModularMenu</span>
            <span className="text-xs text-slate-600">/</span>
          </Link>
          <span className="font-semibold text-sm text-white">The Bombay Canteen</span>
          <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            Active Tenant
          </span>
        </div>

        {/* Viewport Switcher */}
        <div className="flex items-center bg-slate-950 p-1 rounded-lg border border-slate-800">
          <button
            onClick={() => setActiveViewport("mobile")}
            className={`p-1.5 rounded flex items-center gap-1.5 text-xs font-medium transition-colors ${
              activeViewport === "mobile" ? "bg-amber-500 text-slate-950 font-bold" : "text-slate-400 hover:text-white"
            }`}
          >
            <Smartphone className="w-3.5 h-3.5" /> Mobile
          </button>
          <button
            onClick={() => setActiveViewport("tablet")}
            className={`p-1.5 rounded flex items-center gap-1.5 text-xs font-medium transition-colors ${
              activeViewport === "tablet" ? "bg-amber-500 text-slate-950 font-bold" : "text-slate-400 hover:text-white"
            }`}
          >
            <Tablet className="w-3.5 h-3.5" /> Tablet
          </button>
          <button
            onClick={() => setActiveViewport("desktop")}
            className={`p-1.5 rounded flex items-center gap-1.5 text-xs font-medium transition-colors ${
              activeViewport === "desktop" ? "bg-amber-500 text-slate-950 font-bold" : "text-slate-400 hover:text-white"
            }`}
          >
            <Monitor className="w-3.5 h-3.5" /> Desktop
          </button>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-3">
          <Link
            href="/r/the-bombay-canteen"
            target="_blank"
            className="flex items-center gap-1.5 text-xs font-medium text-slate-300 hover:text-white bg-slate-800 hover:bg-slate-700 px-3 py-1.5 rounded-lg transition-colors border border-slate-700"
          >
            <ExternalLink className="w-3.5 h-3.5" /> Public QR Link
          </Link>
          <button
            onClick={handlePublish}
            className="flex items-center gap-1.5 text-xs font-bold bg-amber-500 hover:bg-amber-400 text-slate-950 px-4 py-1.5 rounded-lg transition-all shadow-md shadow-amber-500/10"
          >
            <CheckCircle2 className="w-3.5 h-3.5" /> Publish v{publishVersion}
          </button>
        </div>
      </header>

      {/* 3-Panel Workspace Body */}
      <div className="flex-1 flex overflow-hidden">
        {/* PANEL 1: Left Structure Tree & Catalog Items */}
        <aside className="w-80 border-r border-slate-800 bg-slate-900/60 flex flex-col shrink-0">
          <div className="p-3 border-b border-slate-800 flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
              <Layers className="w-3.5 h-3.5 text-amber-500" /> Catalog Hierarchy
            </span>
            <span className="text-[10px] text-slate-500 font-mono">3 Categories · 6 Items</span>
          </div>

          <div className="flex-1 overflow-y-auto p-3 space-y-4">
            {categories.map((cat) => (
              <div key={cat.id} className="rounded-xl border border-slate-800 bg-slate-950/60 p-3">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-bold text-slate-200">{cat.name}</span>
                  <span className="text-[10px] text-slate-500 font-mono">{cat.items.length} items</span>
                </div>
                <div className="space-y-1.5">
                  {cat.items.map((it) => (
                    <div
                      key={it.id}
                      className="p-2 rounded-lg bg-slate-900 border border-slate-800/80 flex items-center justify-between text-xs"
                    >
                      <div className="truncate pr-2">
                        <div className="font-medium text-slate-200 truncate">{it.name}</div>
                        <div className="text-[11px] text-slate-400 font-mono">₹{it.price}</div>
                      </div>
                      <button
                        onClick={() => toggleAvailability(cat.id, it.id)}
                        className={`text-[10px] px-2 py-0.5 rounded font-mono font-semibold transition-colors shrink-0 ${
                          it.isAvailable
                            ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 hover:bg-emerald-500/20"
                            : "bg-red-500/10 text-red-400 border border-red-500/30 hover:bg-red-500/20"
                        }`}
                      >
                        {it.isAvailable ? "In Stock" : "86'd"}
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </aside>

        {/* PANEL 2: Center Live Viewport Canvas */}
        <main className="flex-1 bg-slate-950 overflow-y-auto flex items-center justify-center p-6">
          <div
            className={`transition-all duration-300 shadow-2xl rounded-2xl overflow-hidden border border-slate-800 flex flex-col ${
              activeViewport === "mobile"
                ? "w-[380px] h-[760px]"
                : activeViewport === "tablet"
                ? "w-[720px] h-[800px]"
                : "w-full max-w-4xl h-full"
            }`}
            style={livePreviewStyles}
          >
            {/* Embedded Live Renderer Screen */}
            <div className="flex-1 overflow-y-auto bg-theme-surface text-theme-text font-body p-4 sm:p-6 transition-colors">
              {/* Restaurant Header */}
              <div className="text-center pb-6 border-b border-theme-border">
                <div className="inline-block px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold tracking-widest uppercase mb-2 bg-theme-muted text-theme-textMuted border border-theme-border">
                  Dinner Tasting
                </div>
                <h1 className="text-2xl sm:text-3xl font-bold font-heading text-theme-primary mb-1">
                  The Bombay Canteen
                </h1>
                <p className="text-xs text-theme-textMuted max-w-xs mx-auto">
                  Modern Indian dining inspired by regional cultures and indigenous ingredients.
                </p>
              </div>

              {/* Category Pills Bar */}
              <div className="flex items-center gap-2 overflow-x-auto py-3 no-scrollbar sticky top-0 bg-theme-surface/90 backdrop-blur-md z-10">
                {categories.map((c) => (
                  <button
                    key={c.id}
                    onClick={() => setSelectedCategory(c.id)}
                    className={`text-xs px-3 py-1.5 rounded-full font-medium whitespace-nowrap transition-all border ${
                      selectedCategory === c.id
                        ? "bg-theme-primary text-theme-primaryForeground border-theme-primary font-bold shadow-sm"
                        : "bg-theme-elevated text-theme-textMuted border-theme-border hover:text-theme-text"
                    }`}
                  >
                    {c.name}
                  </button>
                ))}
              </div>

              {/* Items List */}
              <div className="space-y-3 pt-2">
                {categories
                  .find((c) => c.id === selectedCategory)
                  ?.items.map((item) => (
                    <div
                      key={item.id}
                      className={`p-4 rounded-theme border border-theme-border bg-theme-elevated transition-all ${
                        !item.isAvailable ? "opacity-40 grayscale" : "hover:shadow-md"
                      }`}
                    >
                      <div className="flex items-start justify-between gap-3 mb-1.5">
                        <div className="flex items-center gap-2">
                          {/* FSSAI Dietary Badge */}
                          <div
                            className={`w-3.5 h-3.5 rounded-sm border-2 flex items-center justify-center ${
                              item.dietary === "vegetarian"
                                ? "border-theme-veg"
                                : item.dietary === "egg"
                                ? "border-theme-egg"
                                : "border-theme-nonVeg"
                            }`}
                          >
                            <div
                              className={`w-1.5 h-1.5 rounded-full ${
                                item.dietary === "vegetarian"
                                  ? "bg-theme-veg"
                                  : item.dietary === "egg"
                                  ? "bg-theme-egg"
                                  : "bg-theme-nonVeg"
                              }`}
                            />
                          </div>
                          <span className="font-bold text-sm text-theme-text">{item.name}</span>
                          {item.isFeatured && (
                            <span className="text-[9px] font-bold px-1.5 py-0.5 rounded bg-theme-accent/20 text-theme-accent border border-theme-accent/30 font-mono">
                              SIGNATURE
                            </span>
                          )}
                        </div>
                        <span className="font-price font-bold text-sm text-theme-primary whitespace-nowrap">
                          {formatPrice(item.price)}
                        </span>
                      </div>
                      <p className="text-xs text-theme-textMuted leading-relaxed pr-6">{item.description}</p>
                      {!item.isAvailable && (
                        <div className="mt-2 text-[10px] font-mono text-red-500 font-bold uppercase tracking-wider">
                          Sold Out for this service
                        </div>
                      )}
                    </div>
                  ))}
              </div>
            </div>
          </div>
        </main>

        {/* PANEL 3: Right Theme & Token Inspector */}
        <aside className="w-80 border-l border-slate-800 bg-slate-900/60 flex flex-col shrink-0">
          <div className="p-3 border-b border-slate-800 flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
              <Palette className="w-3.5 h-3.5 text-amber-500" /> Theme Presets
            </span>
            <span className="text-[10px] text-amber-400 font-mono font-bold">{selectedTheme.name}</span>
          </div>

          <div className="flex-1 overflow-y-auto p-4 space-y-6">
            {/* The 6 Visual Themes Grid */}
            <div>
              <label className="text-xs font-semibold text-slate-300 block mb-2">Select Visual Theme</label>
              <div className="grid grid-cols-2 gap-2">
                {THEME_PRESETS.map((preset) => (
                  <button
                    key={preset.theme_key}
                    onClick={() => setSelectedTheme(preset)}
                    className={`p-2.5 rounded-xl border text-left transition-all ${
                      selectedTheme.theme_key === preset.theme_key
                        ? "border-amber-500 bg-amber-500/10 shadow-sm"
                        : "border-slate-800 bg-slate-950/60 hover:border-slate-700"
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-xs font-bold text-white">{preset.name}</span>
                      <div
                        className="w-3.5 h-3.5 rounded-full border border-slate-700 shadow-sm"
                        style={{ backgroundColor: preset.tokens.colors.primary }}
                      />
                    </div>
                    <div className="text-[10px] text-slate-500 font-mono truncate">
                      {preset.tokens.typography.fontHeading}
                    </div>
                  </button>
                ))}
              </div>
            </div>

            {/* Design Token Inspector */}
            <div className="border-t border-slate-800 pt-4 space-y-4">
              <span className="text-xs font-semibold text-slate-300 block">Token Palette Inspector</span>
              
              <div className="space-y-2 text-xs">
                <div className="flex items-center justify-between p-2 rounded-lg bg-slate-950 border border-slate-800">
                  <span className="text-slate-400">Surface Background</span>
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-[11px] text-slate-300">{selectedTheme.tokens.colors.surface}</span>
                    <div
                      className="w-4 h-4 rounded border border-slate-700"
                      style={{ backgroundColor: selectedTheme.tokens.colors.surface }}
                    />
                  </div>
                </div>

                <div className="flex items-center justify-between p-2 rounded-lg bg-slate-950 border border-slate-800">
                  <span className="text-slate-400">Primary Accent</span>
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-[11px] text-slate-300">{selectedTheme.tokens.colors.primary}</span>
                    <div
                      className="w-4 h-4 rounded border border-slate-700"
                      style={{ backgroundColor: selectedTheme.tokens.colors.primary }}
                    />
                  </div>
                </div>

                <div className="flex items-center justify-between p-2 rounded-lg bg-slate-950 border border-slate-800">
                  <span className="text-slate-400">Heading Typography</span>
                  <span className="font-mono text-[11px] text-amber-400">{selectedTheme.tokens.typography.fontHeading}</span>
                </div>

                <div className="flex items-center justify-between p-2 rounded-lg bg-slate-950 border border-slate-800">
                  <span className="text-slate-400">Card Radius</span>
                  <span className="font-mono text-[11px] text-slate-300">{selectedTheme.tokens.layout.borderRadius}</span>
                </div>
              </div>
            </div>

            {/* Publication Feedback Banner */}
            {isPublished && (
              <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs animate-fade-in flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 shrink-0 text-emerald-400" />
                <span>
                  <strong>Published v{publishVersion}!</strong> Snapshot compiled with SHA-256 hash. Customer QR updated.
                </span>
              </div>
            )}
          </div>
        </aside>
      </div>
    </div>
  );
}
