"use client";

import React, { useState } from "react";
import Link from "next/link";
import {
  Search,
  Sparkles,
  Flame,
  Leaf,
  Beef,
  Egg,
  Info,
  ChevronRight,
  Share2,
  X,
} from "lucide-react";
import { THEME_PRESETS, generateCssVariables } from "@/lib/themes";
import { formatPrice } from "@/lib/utils";

// Sample Public Published Menu Data for The Bombay Canteen
const MENU_DATA = {
  restaurant: {
    name: "The Bombay Canteen",
    slug: "the-bombay-canteen",
    description: "Modern Indian dining celebrating regional cultures and indigenous seasonal produce.",
    address: "Process House, Kamala Mills, Lower Parel, Mumbai",
    currency: "INR",
  },
  theme: THEME_PRESETS[0], // Luxury Preset
  categories: [
    {
      id: "small-plates",
      name: "Small Plates & Chintu",
      description: "Quick, flavorful bites inspired by Indian street culture and community feasts.",
      items: [
        {
          id: "item-1",
          name: "Barley & Jowar Salad",
          description: "Pomegranate seeds, spiced hung curd dressing, crispy sev, puffed amaranth.",
          price: 425,
          dietary: "vegetarian",
          spice: "mild",
          allergens: ["Dairy"],
          isAvailable: true,
          isFeatured: true,
        },
        {
          id: "item-2",
          name: "Chettinad Fried Chicken",
          description: "Curry leaf crisp, shallot chutney dip, buttermilk batter, crushed black pepper.",
          price: 525,
          dietary: "non_veg",
          spice: "hot",
          allergens: ["Gluten", "Dairy"],
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
          allergens: ["Gluten", "Dairy", "Egg"],
          isAvailable: true,
        },
      ],
    },
    {
      id: "big-plates",
      name: "Big Plates & Curries",
      description: "Hearty traditional curries cooked with regional spices and artisanal techniques.",
      items: [
        {
          id: "item-4",
          name: "Paneer & Fig Kofta",
          description: "Almond yogurt gravy, fenugreek cream, served with flaky malabar parotta.",
          price: 650,
          dietary: "vegetarian",
          spice: "mild",
          allergens: ["Dairy", "Nuts"],
          isAvailable: true,
        },
        {
          id: "item-5",
          name: "Kerala Roast Duck",
          description: "Slow-roasted duck leg, tellicherry black pepper, shallots, coconut oil drizzle.",
          price: 895,
          dietary: "non_veg",
          spice: "hot",
          allergens: [],
          isAvailable: true,
        },
      ],
    },
    {
      id: "breads-rice",
      name: "Breads & Rice",
      description: "Tandoor baked breads and heirloom grain preparations.",
      items: [
        {
          id: "item-6",
          name: "Truffle & Wild Mushroom Kulcha",
          description: "Smoked scamorza cheese, fresh coriander butter, black truffle glaze.",
          price: 375,
          dietary: "vegetarian",
          spice: "none",
          allergens: ["Gluten", "Dairy"],
          isAvailable: true,
          isFeatured: true,
        },
      ],
    },
  ],
};

export default function CustomerMenuPage({ params }: { params: { slug: string } }) {
  const [activeCategory, setActiveCategory] = useState<string>("small-plates");
  const [dietaryFilter, setDietaryFilter] = useState<string>("all");
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [selectedItem, setSelectedItem] = useState<any | null>(null);

  const themeStyles = generateCssVariables(MENU_DATA.theme.tokens);

  // Filter items based on dietary tag and search query
  const filteredCategories = MENU_DATA.categories
    .map((cat) => ({
      ...cat,
      items: cat.items.filter((item) => {
        const matchesDietary =
          dietaryFilter === "all" ||
          (dietaryFilter === "veg" && item.dietary === "vegetarian") ||
          (dietaryFilter === "nonveg" && item.dietary === "non_veg") ||
          (dietaryFilter === "egg" && item.dietary === "egg");

        const matchesSearch =
          item.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
          item.description.toLowerCase().includes(searchQuery.toLowerCase());

        return matchesDietary && matchesSearch;
      }),
    }))
    .filter((cat) => cat.items.length > 0);

  return (
    <div
      className="min-h-screen bg-theme-surface text-theme-text font-body selection:bg-theme-accent selection:text-white"
      style={themeStyles}
    >
      {/* Top Banner / Restaurant Header */}
      <header className="px-4 pt-8 pb-6 text-center border-b border-theme-border bg-theme-surface">
        <div className="max-w-md mx-auto">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-theme-muted border border-theme-border text-[11px] font-mono uppercase tracking-wider text-theme-textMuted mb-3">
            <Sparkles className="w-3 h-3 text-theme-primary" /> Verified Digital Menu
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold font-heading text-theme-primary tracking-tight mb-1.5">
            {MENU_DATA.restaurant.name}
          </h1>
          <p className="text-xs text-theme-textMuted leading-relaxed max-w-sm mx-auto mb-3">
            {MENU_DATA.restaurant.description}
          </p>
          <div className="text-[11px] text-theme-textMuted flex items-center justify-center gap-1">
            <span>{MENU_DATA.restaurant.address}</span>
          </div>
        </div>
      </header>

      {/* Sticky Search & Dietary Filter Section */}
      <div className="sticky top-0 z-20 bg-theme-surface/95 backdrop-blur-md border-b border-theme-border px-4 py-3">
        <div className="max-w-md mx-auto space-y-2.5">
          {/* Search Input */}
          <div className="relative">
            <Search className="w-4 h-4 text-theme-textMuted absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search dishes, ingredients, allergens..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-theme-elevated text-theme-text text-xs rounded-theme pl-9 pr-4 py-2 border border-theme-border placeholder:text-theme-textMuted focus:outline-none focus:border-theme-primary"
            />
          </div>

          {/* FSSAI Dietary Filter Pills */}
          <div className="flex items-center gap-1.5 overflow-x-auto no-scrollbar">
            <button
              onClick={() => setDietaryFilter("all")}
              className={`text-xs px-3 py-1 rounded-full font-medium whitespace-nowrap transition-all border ${
                dietaryFilter === "all"
                  ? "bg-theme-primary text-theme-primaryForeground border-theme-primary font-bold shadow-sm"
                  : "bg-theme-elevated text-theme-textMuted border-theme-border"
              }`}
            >
              All Dishes
            </button>
            <button
              onClick={() => setDietaryFilter("veg")}
              className={`text-xs px-3 py-1 rounded-full font-medium whitespace-nowrap transition-all border flex items-center gap-1.5 ${
                dietaryFilter === "veg"
                  ? "bg-emerald-600 text-white border-emerald-600 font-bold shadow-sm"
                  : "bg-theme-elevated text-theme-textMuted border-theme-border hover:border-emerald-500"
              }`}
            >
              <div className="w-2 h-2 rounded-full bg-emerald-500" /> Pure Veg
            </button>
            <button
              onClick={() => setDietaryFilter("nonveg")}
              className={`text-xs px-3 py-1 rounded-full font-medium whitespace-nowrap transition-all border flex items-center gap-1.5 ${
                dietaryFilter === "nonveg"
                  ? "bg-red-600 text-white border-red-600 font-bold shadow-sm"
                  : "bg-theme-elevated text-theme-textMuted border-theme-border hover:border-red-500"
              }`}
            >
              <div className="w-2 h-2 rounded-full bg-red-500" /> Non-Veg
            </button>
            <button
              onClick={() => setDietaryFilter("egg")}
              className={`text-xs px-3 py-1 rounded-full font-medium whitespace-nowrap transition-all border flex items-center gap-1.5 ${
                dietaryFilter === "egg"
                  ? "bg-amber-600 text-white border-amber-600 font-bold shadow-sm"
                  : "bg-theme-elevated text-theme-textMuted border-theme-border hover:border-amber-500"
              }`}
            >
              <div className="w-2 h-2 rounded-full bg-amber-500" /> Contains Egg
            </button>
          </div>
        </div>
      </div>

      {/* Main Menu List */}
      <main className="max-w-md mx-auto px-4 py-6 space-y-8">
        {filteredCategories.map((category) => (
          <section key={category.id} id={category.id} className="scroll-mt-28">
            <div className="mb-3">
              <h2 className="text-lg font-bold font-heading text-theme-primary tracking-tight">
                {category.name}
              </h2>
              {category.description && (
                <p className="text-xs text-theme-textMuted leading-relaxed">{category.description}</p>
              )}
            </div>

            <div className="space-y-3">
              {category.items.map((item) => (
                <div
                  key={item.id}
                  onClick={() => setSelectedItem(item)}
                  className="p-4 rounded-theme border border-theme-border bg-theme-elevated shadow-sm hover:border-theme-primary/40 transition-all cursor-pointer"
                >
                  <div className="flex items-start justify-between gap-3 mb-1.5">
                    <div className="flex items-center gap-2">
                      {/* Dietary FSSAI indicator */}
                      <div
                        className={`w-3.5 h-3.5 rounded-sm border-2 flex items-center justify-center shrink-0 ${
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
                      <span className="font-bold text-sm text-theme-text leading-snug">{item.name}</span>
                      {item.isFeatured && (
                        <span className="text-[9px] font-bold px-1.5 py-0.5 rounded bg-theme-accent/20 text-theme-accent border border-theme-accent/30 font-mono">
                          CHEF'S PICK
                        </span>
                      )}
                    </div>
                    <span className="font-price font-bold text-sm text-theme-primary whitespace-nowrap">
                      {formatPrice(item.price)}
                    </span>
                  </div>

                  <p className="text-xs text-theme-textMuted leading-relaxed line-clamp-2 pr-4">
                    {item.description}
                  </p>

                  {/* Badges / Spice Level */}
                  <div className="mt-2.5 flex items-center gap-2 text-[10px] text-theme-textMuted">
                    {item.spice !== "none" && (
                      <span className="flex items-center gap-0.5 text-amber-500 font-medium">
                        <Flame className="w-3 h-3 fill-amber-500" />
                        <span className="capitalize">{item.spice} Spice</span>
                      </span>
                    )}
                    {item.allergens && item.allergens.length > 0 && (
                      <span className="text-slate-500 font-mono">Contains: {item.allergens.join(", ")}</span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </section>
        ))}
      </main>

      {/* Item Detail Modal / Bottom Sheet */}
      {selectedItem && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-end sm:items-center justify-center p-0 sm:p-4 animate-fade-in">
          <div className="w-full max-w-md bg-theme-surface border border-theme-border rounded-t-2xl sm:rounded-theme p-6 shadow-2xl relative">
            <button
              onClick={() => setSelectedItem(null)}
              className="absolute right-4 top-4 p-1.5 rounded-full bg-theme-elevated text-theme-textMuted hover:text-theme-text border border-theme-border"
            >
              <X className="w-4 h-4" />
            </button>

            <div className="flex items-center gap-2 mb-2">
              <div
                className={`w-3.5 h-3.5 rounded-sm border-2 flex items-center justify-center ${
                  selectedItem.dietary === "vegetarian"
                    ? "border-theme-veg"
                    : selectedItem.dietary === "egg"
                    ? "border-theme-egg"
                    : "border-theme-nonVeg"
                }`}
              >
                <div
                  className={`w-1.5 h-1.5 rounded-full ${
                    selectedItem.dietary === "vegetarian"
                      ? "bg-theme-veg"
                      : selectedItem.dietary === "egg"
                      ? "bg-theme-egg"
                      : "bg-theme-nonVeg"
                  }`}
                />
              </div>
              <h3 className="font-heading font-bold text-lg text-theme-text">{selectedItem.name}</h3>
            </div>

            <div className="text-lg font-bold font-price text-theme-primary mb-3">
              {formatPrice(selectedItem.price)}
            </div>

            <p className="text-xs text-theme-textMuted leading-relaxed mb-4">
              {selectedItem.description}
            </p>

            {selectedItem.allergens && selectedItem.allergens.length > 0 && (
              <div className="p-3 rounded-theme bg-theme-elevated border border-theme-border mb-4">
                <span className="text-[11px] font-bold text-theme-text block mb-1 flex items-center gap-1.5">
                  <Info className="w-3.5 h-3.5 text-amber-500" /> Allergen Advisory
                </span>
                <span className="text-xs text-theme-textMuted">
                  This dish contains: {selectedItem.allergens.join(", ")}. Please inform your server of any severe food allergies.
                </span>
              </div>
            )}

            <button
              onClick={() => setSelectedItem(null)}
              className="w-full py-2.5 rounded-theme bg-theme-primary text-theme-primaryForeground font-bold text-xs uppercase tracking-wider hover:opacity-90 transition-opacity"
            >
              Close Details
            </button>
          </div>
        </div>
      )}

      {/* Footer */}
      <footer className="border-t border-theme-border py-8 text-center text-xs text-theme-textMuted bg-theme-surface">
        <p className="mb-1 font-mono text-[11px]">Powered by ModularMenu Platform</p>
        <p className="text-[10px] text-slate-500">All prices exclusive of applicable government taxes & service charges.</p>
      </footer>
    </div>
  );
}
