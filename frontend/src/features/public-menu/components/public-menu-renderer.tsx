"use client";

import React, { useState } from "react";
import type { MenuRenderInput } from "@modularmenu/contracts";
import { composeMenu } from "../../../lib/rendering";
import { ThemeScope } from "../../customization/components/ThemeScope";
import { MenuRenderErrorBoundary } from "./menu-render-error-boundary";
import { RestaurantHeader } from "./restaurant-header";
import { MenuHeader } from "./menu-header";
import { CategoryNavigation } from "./category-navigation";
import { CategorySection } from "./category-section";
import { MenuFooter } from "./menu-footer";

interface PublicMenuRendererProps {
  input: MenuRenderInput;
}

export function PublicMenuRenderer({ input }: PublicMenuRendererProps) {
  const { restaurant, menu, resolved_configuration, metadata } = input;
  const layoutId = resolved_configuration?.layout?.id || "layout-grid";
  const tokens = resolved_configuration?.theme?.tokens || {};

  const composition = composeMenu(
    restaurant.name,
    menu.title,
    menu.categories,
    menu.description
  );

  const [activeCategory, setActiveCategory] = useState<string>(
    composition.categories[0]?.id || ""
  );

  return (
    <MenuRenderErrorBoundary>
      <ThemeScope tokens={tokens}>
        <div className="public-menu min-h-screen bg-[var(--mm-color-surface-subtle,#FAFAFA)] text-[var(--mm-color-text-primary,#09090B)] font-[var(--mm-typography-fontFamily-body,sans-serif)] antialiased">
          <RestaurantHeader restaurant={restaurant} />
          <MenuHeader menu={menu} />

          {composition.navigation.length > 1 && (
            <CategoryNavigation
              items={composition.navigation}
              activeId={activeCategory}
              onSelect={setActiveCategory}
            />
          )}

          <main className="public-menu__content">
            {composition.categories.map((category) => (
              <CategorySection
                key={category.id}
                category={category}
                layoutId={layoutId}
                locale={metadata.locale}
              />
            ))}
          </main>

          <MenuFooter restaurant={restaurant} />
        </div>
      </ThemeScope>
    </MenuRenderErrorBoundary>
  );
}
