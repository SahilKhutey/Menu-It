import React from "react";
import type { RenderRestaurant } from "@modularmenu/contracts";
import { MenuImage } from "./menu-image";

interface RestaurantHeaderProps {
  restaurant: RenderRestaurant;
}

export function RestaurantHeader({ restaurant }: RestaurantHeaderProps) {
  return (
    <header className="restaurant-header relative w-full border-b border-[var(--mm-color-border-subtle,#F4F4F5)] bg-[var(--mm-color-surface-default,#FFFFFF)]">
      {restaurant.cover_image && (
        <div className="restaurant-header__cover w-full h-36 md:h-48 overflow-hidden bg-zinc-900">
          <MenuImage
            src={restaurant.cover_image.url}
            alt={restaurant.cover_image.alt || restaurant.name}
            width={restaurant.cover_image.width}
            height={restaurant.cover_image.height}
            priority={true}
          />
        </div>
      )}

      <div className="max-w-4xl mx-auto px-4 py-4 flex items-center gap-4">
        {restaurant.logo && (
          <div className="w-16 h-16 rounded-full overflow-hidden border-2 border-white shadow-md flex-shrink-0 bg-white">
            <MenuImage
              src={restaurant.logo.url}
              alt={restaurant.logo.alt || restaurant.name}
              width={restaurant.logo.width}
              height={restaurant.logo.height}
            />
          </div>
        )}
        <div>
          <h1 className="text-xl md:text-2xl font-bold tracking-tight text-[var(--mm-color-text-primary,#09090B)] font-[var(--mm-typography-fontFamily-heading,inherit)]">
            {restaurant.name}
          </h1>
          {restaurant.description && (
            <p className="text-xs md:text-sm text-[var(--mm-color-text-secondary,#71717A)] mt-0.5 line-clamp-2">
              {restaurant.description}
            </p>
          )}
        </div>
      </div>
    </header>
  );
}
