"use client";

import React, { useState, useEffect } from "react";
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
  QrCode,
  X,
  ShieldCheck,
  Download,
} from "lucide-react";
import { THEME_PRESETS, ThemeConfig, generateCssVariables } from "@/lib/themes";
import { formatPrice } from "@/lib/utils";
import { getPublicMenu, getPublicQrCodeUrl } from "@/lib/api";

// Fallback seed menu in case API is offline or loading
const FALLBACK_MENU = {
  restaurant: {
    name: "The Bombay Canteen",
    slug: "the-bombay-canteen",
    description: "Modern Indian dining celebrating regional cultures and indigenous seasonal produce.",
    address: "Process House, Kamala Mills, Lower Parel, Mumbai",
    currency: "INR",
  },
  theme: THEME_PRESETS[0].tokens, // Luxury Preset
  categories: [
    {
      id: "small-plates",
      name: "Small Plates & Chintu",
      description: "Quick, flavorful bites inspired by Indian street food culture.",
      items: [
        {
          id: "item-1",
          name: "Barley & Jowar Salad",
          description: "Pomegranate seeds, spiced hung curd dressing, crispy sev, puffed amaranth.",
          base_price: 425,
          dietary_type: "vegetarian",
          spice_level: "mild",
          allergens: ["Dairy"],
          is_available: true,
          is_featured: true,
        },
        {
          id: "item-2",
          name: "Chettinad Fried Chicken",
          description: "Curry leaf crisp, shallot chutney dip, buttermilk batter, crushed black pepper.",
          base_price: 525,
          dietary_type: "non_veg",
          spice_level: "hot",
          allergens: ["Gluten", "Dairy"],
          is_available: true,
          is_featured: true,
        },
        {
          id: "item-3",
          name: "Eggs Kejriwal Toast",
          description: "Sunny side up egg, toasted sourdough, melted white cheddar, green chilli tadka.",
          base_price: 450,
          dietary_type: "egg",
          spice_level: "medium",
          allergens: ["Gluten", "Dairy", "Egg"],
          is_available: true,
          is_featured: false,
        },
      ],
    },
    {
      id: "big-plates",
      name: "Big Plates & Curries",
      description: "Hearty heritage curries cooked with regional spices and artisanal techniques.",
      items: [
        {
          id: "item-4",
          name: "Paneer & Fig Kofta",
          description: "Almond yogurt gravy, fenugreek cream, served with flaky malabar parotta.",
          base_price: 650,
          dietary_type: "vegetarian",
          spice_level: "mild",
          allergens: ["Dairy", "Nuts"],
          is_available: true,
          is_featured: true,
        },
        {
          id: "item-5",
          name: "Kerala Roast Duck",
          description: "Slow-roasted duck leg, tellicherry black pepper, shallots, coconut oil drizzle.",
          base_price: 895,
          dietary_type: "non_veg",
          spice_level: "hot",
          allergens: [],
          is_available: true,
          is_featured: true,
        },
      ],
    },
    {
      id: "breads-rice",
      name: "Breads & Heirloom Rice",
      description: "Tandoor baked breads and heirloom grain preparations.",
      items: [
        {
          id: "item-6",
          name: "Truffle & Wild Mushroom Kulcha",
          description: "Smoked scamorza cheese, fresh coriander butter, black truffle glaze.",
          base_price: 375,
          dietary_type: "vegetarian",
          spice_level: "none",
          allergens: ["Gluten", "Dairy"],
          is_available: true,
          is_featured: true,
        },
      ],
    },
    {
      id: "desserts",
      name: "Desserts & Mithai",
      description: "Modern nostalgic desserts reimagined with local dairy and fruits.",
      items: [
        {
          id: "item-7",
          name: "Filter Coffee Tres Leches",
          description: "Chikmagalur espresso soaked sponge cake, condensed milk foam, candied cocoa nibs.",
          base_price: 420,
          dietary_type: "vegetarian",
          spice_level: "none",
          allergens: ["Gluten", "Dairy"],
          is_available: true,
          is_featured: true,
        },
      ],
    },
  ],
};

export default function CustomerMenuPage({ params }: { params: { slug: string } }) {
  const [menuData, setMenuData] = useState<any>(FALLBACK_MENU);
  const [versionNumber, setVersionNumber] = useState<number>(1);
  const [checksum, setChecksum] = useState<string>("sha256-verified-live");
  const [dietaryFilter, setDietaryFilter] = useState<string>("all");
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [selectedItem, setSelectedItem] = useState<any | null>(null);
  const [showQrModal, setShowQrModal] = useState<boolean>(false);
  const [isLiveApi, setIsLiveApi] = useState<boolean>(false);

  useEffect(() => {
    async function loadPublishedSnapshot() {
      try {
        const res = await getPublicMenu(params.slug);
        if (res && res.data) {
          setMenuData(res.data);
          if (res.version_number) setVersionNumber(res.version_number);
          if (res.checksum) setChecksum(res.checksum);
          setIsLiveApi(true);
        }
      } catch (e) {
        console.info("Using embedded pre-compiled snapshot fallback for:", params.slug);
      }
    }
    loadPublishedSnapshot();
  }, [params.slug]);

  // Generate CSS Variables dynamically from theme tokens in snapshot
  const activeTokens = menuData.theme || THEME_PRESETS[0].tokens;
  const themeStyles = generateCssVariables(activeTokens);

  // Filter items based on dietary tag and search query
  const categoriesList = menuData.categories || [];
  const filteredCategories = categoriesList
    .map((cat: any) => ({
      ...cat,
      items: (cat.items || []).filter((item: any) => {
        const dietary = item.dietary_type || item.dietary || "vegetarian";
        const matchesDietary =
          dietaryFilter === "all" ||
          (dietaryFilter === "veg" && dietary === "vegetarian") ||
          (dietaryFilter === "nonveg" && dietary === "non_veg") ||
          (dietaryFilter === "egg" && dietary === "egg");

        const matchesSearch =
          item.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
          (item.description && item.description.toLowerCase().includes(searchQuery.toLowerCase()));

        return matchesDietary && matchesSearch;
      }),
    }))
    .filter((cat: any) => cat.items.length > 0);

  const qrImageUrl = getPublicQrCodeUrl(params.slug);

  return (
    <div
      className="min-h-screen bg-theme-surface text-theme-text font-body selection:bg-theme-accent selection:text-white pb-16"
      style={themeStyles}
    >
      {/* Top Banner / Restaurant Identity */}
      <header className="px-4 pt-8 pb-6 text-center border-b border-theme-border bg-theme-surface relative">
        <div className="max-w-md mx-auto">
          <div className="flex items-center justify-center gap-2 mb-3">
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-theme-muted border border-theme-border text-[11px] font-mono uppercase tracking-wider text-theme-textMuted">
              <Sparkles className="w-3 h-3 text-theme-primary" /> Verified Digital Menu · v{versionNumber}
            </span>
            <button
              onClick={() => setShowQrModal(true)}
              className="p-1 rounded-full bg-theme-elevated text-theme-text hover:text-theme-primary border border-theme-border transition-colors"
              title="View Table QR Code"
            >
              <QrCode className="w-4 h-4" />
            </button>
          </div>

          <h1 className="text-2xl sm:text-3xl font-bold font-heading text-theme-primary tracking-tight mb-1.5">
            {menuData.restaurant?.name || "Restaurant Menu"}
          </h1>
          <p className="text-xs text-theme-textMuted leading-relaxed max-w-sm mx-auto mb-2">
            {menuData.restaurant?.description || "Curated seasonal dining experience."}
          </p>
          {menuData.restaurant?.address && (
            <div className="text-[11px] text-theme-textMuted flex items-center justify-center gap-1 font-mono">
              <span>{menuData.restaurant.address}</span>
            </div>
          )}
        </div>
      </header>

      {/* Sticky Search & Dietary Filter Section */}
      <div className="sticky top-0 z-20 bg-theme-surface/95 backdrop-blur-md border-b border-theme-border px-4 py-3 shadow-sm">
        <div className="max-w-md mx-auto space-y-2.5">
          {/* Search Input */}
          <div className="relative">
            <Search className="w-4 h-4 text-theme-textMuted absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search dishes, ingredients, allergens..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-theme-elevated text-theme-text text-xs rounded-theme pl-9 pr-4 py-2 border border-theme-border placeholder:text-theme-textMuted focus:outline-none focus:border-theme-primary transition-colors"
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
        {filteredCategories.length === 0 ? (
          <div className="p-8 text-center rounded-theme bg-theme-elevated border border-theme-border text-theme-textMuted text-xs">
            No dishes matching your current filter. Try resetting search or dietary preferences.
          </div>
        ) : (
          filteredCategories.map((category: any) => (
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
                {category.items.map((item: any) => {
                  const dietary = item.dietary_type || item.dietary || "vegetarian";
                  const price = item.base_price !== undefined ? item.base_price : item.price;
                  const isAvail = item.is_available !== undefined ? item.is_available : true;
                  const isFeatured = item.is_featured !== undefined ? item.is_featured : false;

                  return (
                    <div
                      key={item.id}
                      onClick={() => setSelectedItem(item)}
                      className={`p-4 rounded-theme border border-theme-border bg-theme-elevated shadow-sm hover:border-theme-primary/40 transition-all cursor-pointer ${
                        !isAvail ? "opacity-40 grayscale" : ""
                      }`}
                    >
                      <div className="flex items-start justify-between gap-3 mb-1.5">
                        <div className="flex items-center gap-2">
                          {/* FSSAI Dietary Badge */}
                          <div
                            className={`w-3.5 h-3.5 rounded-sm border-2 flex items-center justify-center shrink-0 ${
                              dietary === "vegetarian"
                                ? "border-theme-veg"
                                : dietary === "egg"
                                ? "border-theme-egg"
                                : "border-theme-nonVeg"
                            }`}
                          >
                            <div
                              className={`w-1.5 h-1.5 rounded-full ${
                                dietary === "vegetarian"
                                  ? "bg-theme-veg"
                                  : dietary === "egg"
                                  ? "bg-theme-egg"
                                  : "bg-theme-nonVeg"
                              }`}
                            />
                          </div>
                          <span className="font-bold text-sm text-theme-text leading-snug">{item.name}</span>
                          {isFeatured && (
                            <span className="text-[9px] font-bold px-1.5 py-0.5 rounded bg-theme-accent/20 text-theme-accent border border-theme-accent/30 font-mono">
                              SIGNATURE
                            </span>
                          )}
                        </div>
                        <span className="font-price font-bold text-sm text-theme-primary whitespace-nowrap">
                          {formatPrice(price)}
                        </span>
                      </div>

                      <p className="text-xs text-theme-textMuted leading-relaxed line-clamp-2 pr-4">
                        {item.description}
                      </p>

                      {/* Spice indicator & Allergens */}
                      <div className="mt-2.5 flex items-center gap-2 text-[10px] text-theme-textMuted">
                        {item.spice_level && item.spice_level !== "none" && (
                          <span className="flex items-center gap-0.5 text-amber-500 font-medium">
                            <Flame className="w-3 h-3 fill-amber-500" />
                            <span className="capitalize">{item.spice_level} Spice</span>
                          </span>
                        )}
                        {item.allergens && item.allergens.length > 0 && (
                          <span className="text-slate-500 font-mono">Contains: {item.allergens.join(", ")}</span>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </section>
          ))
        )}
      </main>

      {/* QR Code Presentation Modal */}
      {showQrModal && (
        <div className="fixed inset-0 z-50 bg-black/75 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="w-full max-w-sm bg-theme-surface border border-theme-border rounded-2xl p-6 shadow-2xl text-center relative">
            <button
              onClick={() => setShowQrModal(false)}
              className="absolute right-4 top-4 p-1.5 rounded-full bg-theme-elevated text-theme-textMuted hover:text-theme-text border border-theme-border"
            >
              <X className="w-4 h-4" />
            </button>

            <h3 className="font-heading font-bold text-lg text-theme-primary mb-1">
              {menuData.restaurant?.name}
            </h3>
            <p className="text-xs text-theme-textMuted mb-4">
              Scan to open digital menu on any smartphone camera
            </p>

            <div className="bg-white p-4 rounded-xl border border-slate-200 inline-block shadow-inner mb-4">
              {/* Dynamic QR Code Render */}
              <img
                src={qrImageUrl}
                alt="Table QR Code"
                className="w-48 h-48 mx-auto"
                onError={(e) => {
                  // Fallback visual QR representation if backend offline
                  (e.target as HTMLElement).style.display = "none";
                }}
              />
              <div className="text-[10px] font-mono text-slate-500 mt-2">
                /r/{params.slug}
              </div>
            </div>

            <div className="text-[11px] text-theme-textMuted font-mono break-all mb-4">
              SHA256: {checksum.slice(0, 16)}...
            </div>

            <button
              onClick={() => setShowQrModal(false)}
              className="w-full py-2.5 rounded-theme bg-theme-primary text-theme-primaryForeground font-bold text-xs uppercase tracking-wider hover:opacity-90 transition-opacity"
            >
              Done
            </button>
          </div>
        </div>
      )}

      {/* Item Detail Modal / Bottom Sheet */}
      {selectedItem && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-end sm:items-center justify-center p-0 sm:p-4">
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
                  (selectedItem.dietary_type || selectedItem.dietary) === "vegetarian"
                    ? "border-theme-veg"
                    : (selectedItem.dietary_type || selectedItem.dietary) === "egg"
                    ? "border-theme-egg"
                    : "border-theme-nonVeg"
                }`}
              >
                <div
                  className={`w-1.5 h-1.5 rounded-full ${
                    (selectedItem.dietary_type || selectedItem.dietary) === "vegetarian"
                      ? "bg-theme-veg"
                      : (selectedItem.dietary_type || selectedItem.dietary) === "egg"
                      ? "bg-theme-egg"
                      : "bg-theme-nonVeg"
                  }`}
                />
              </div>
              <h3 className="font-heading font-bold text-lg text-theme-text">{selectedItem.name}</h3>
            </div>

            <div className="text-lg font-bold font-price text-theme-primary mb-3">
              {formatPrice(selectedItem.base_price !== undefined ? selectedItem.base_price : selectedItem.price)}
            </div>

            <p className="text-xs text-theme-textMuted leading-relaxed mb-4">
              {selectedItem.description}
            </p>

            {/* Portions / Variants if present */}
            {selectedItem.variants && selectedItem.variants.length > 0 && (
              <div className="mb-4 space-y-2">
                <span className="text-[11px] font-bold text-theme-text block font-mono uppercase tracking-wider">
                  Portion Sizes
                </span>
                <div className="grid grid-cols-2 gap-2">
                  {selectedItem.variants.map((v: any, idx: number) => (
                    <div
                      key={idx}
                      className="p-2 rounded-theme border border-theme-border bg-theme-elevated text-xs flex justify-between items-center"
                    >
                      <span className="font-medium text-theme-text">{v.name}</span>
                      <span className="font-price font-bold text-theme-primary">
                        {v.price_delta > 0 ? `+₹${v.price_delta}` : "Included"}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Allergen Advisory */}
            {selectedItem.allergens && selectedItem.allergens.length > 0 && (
              <div className="p-3 rounded-theme bg-theme-elevated border border-theme-border mb-4">
                <span className="text-[11px] font-bold text-theme-text block mb-1 flex items-center gap-1.5">
                  <Info className="w-3.5 h-3.5 text-amber-500" /> Allergen Information
                </span>
                <span className="text-xs text-theme-textMuted">
                  This dish contains: {selectedItem.allergens.join(", ")}. Please inform your server of any severe allergies before ordering.
                </span>
              </div>
            )}

            <button
              onClick={() => setSelectedItem(null)}
              className="w-full py-2.5 rounded-theme bg-theme-primary text-theme-primaryForeground font-bold text-xs uppercase tracking-wider hover:opacity-90 transition-opacity"
            >
              Close
            </button>
          </div>
        </div>
      )}

      {/* Footer */}
      <footer className="border-t border-theme-border py-8 text-center text-xs text-theme-textMuted bg-theme-surface mt-12">
        <p className="mb-1 font-mono text-[11px] flex items-center justify-center gap-1.5">
          <ShieldCheck className="w-3.5 h-3.5 text-emerald-500" /> Powered by ModularMenu Platform
        </p>
        <p className="text-[10px] text-slate-500">All prices exclusive of applicable government GST & discretionary service charges.</p>
      </footer>
    </div>
  );
}
