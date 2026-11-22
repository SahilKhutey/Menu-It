import React from "react";
import type { RenderCategory } from "@modularmenu/contracts";
import { FoodItemCard } from "./food-item-card";

interface CategorySectionProps {
  category: RenderCategory;
  layoutId?: string;
  locale?: string;
}

export function CategorySection({
  category,
  layoutId = "layout-grid",
  locale = "en-IN",
}: CategorySectionProps) {
  const visibleItems = (category.items || []).filter((item) => item.availability !== "unavailable");

  if (visibleItems.length === 0) {
    return null;
  }

  const gridClass =
    layoutId === "layout-list"
      ? "grid grid-cols-1 gap-3"
      : layoutId === "layout-image-cards"
      ? "grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4"
      : "grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4";

  return (
    <section
      id={`category-${encodeURIComponent(category.id)}`}
      className="category-section max-w-4xl mx-auto px-4 py-6 scroll-mt-14"
      aria-labelledby={`heading-${category.id}`}
    >
      <div className="mb-4 border-b border-[var(--mm-color-border-subtle,#F4F4F5)] pb-2">
        <h3
          id={`heading-${category.id}`}
          className="text-lg md:text-xl font-bold text-[var(--mm-color-text-primary,#09090B)] font-[var(--mm-typography-fontFamily-heading,inherit)]"
        >
          {category.name}
        </h3>
        {category.description && (
          <p className="text-xs text-[var(--mm-color-text-secondary,#71717A)] mt-0.5">
            {category.description}
          </p>
        )}
      </div>

      <div className={gridClass}>
        {visibleItems.map((item) => (
          <FoodItemCard
            key={item.id}
            item={item}
            locale={locale}
            cardStyle={layoutId === "layout-list" ? "flat" : "elevated"}
          />
        ))}
      </div>
    </section>
  );
}
