import React from "react";
import type { RenderMenuItem } from "@modularmenu/contracts";
import { formatPrice } from "../../../lib/rendering";
import { MenuImage } from "./menu-image";

interface FoodItemCardProps {
  item: RenderMenuItem;
  locale?: string;
  showDescription?: boolean;
  showPrice?: boolean;
  showAvailability?: boolean;
  showImage?: boolean;
  cardStyle?: "flat" | "elevated" | "bordered";
}

export function FoodItemCard({
  item,
  locale = "en-IN",
  showDescription = true,
  showPrice = true,
  showAvailability = true,
  showImage = true,
  cardStyle = "elevated",
}: FoodItemCardProps) {
  const isAvailable = item.availability === "available";
  const isSoldOut = item.availability === "sold_out";

  const primaryImage = item.images && item.images.length > 0 ? item.images[0] : null;

  return (
    <article
      className={`menu-item-card menu-item-card--${cardStyle} rounded-xl overflow-hidden transition-all duration-200 ${
        isAvailable ? "opacity-100" : "opacity-75"
      }`}
      data-item-id={item.id}
      data-availability={item.availability}
      aria-label={`${item.name}${item.price ? `, ${formatPrice(item.price.amount_minor, item.price.currency, locale)}` : ""}`}
    >
      {showImage && primaryImage && (
        <div className="menu-item-card__media relative w-full overflow-hidden bg-zinc-100">
          <MenuImage
            src={primaryImage.url}
            alt={primaryImage.alt || item.name}
            width={primaryImage.width}
            height={primaryImage.height}
          />
          {isSoldOut && (
            <span className="absolute top-2 right-2 bg-rose-600 text-white text-xs font-bold px-2 py-1 rounded shadow">
              Sold Out
            </span>
          )}
        </div>
      )}

      <div className="menu-item-card__content p-4 flex flex-col justify-between flex-grow">
        <div>
          <div className="flex items-start justify-between gap-2">
            <h4 className="text-base font-semibold leading-snug text-[var(--mm-color-text-primary,#09090B)]">
              {item.name}
            </h4>
            {showPrice && item.price && (
              <span className="text-sm font-bold tracking-tight text-[var(--mm-color-brand-primary,#18181B)] whitespace-nowrap">
                {formatPrice(item.price.amount_minor, item.price.currency, locale)}
              </span>
            )}
          </div>

          {showDescription && item.description && (
            <p className="mt-1 text-xs text-[var(--mm-color-text-secondary,#71717A)] line-clamp-2 leading-relaxed">
              {item.description}
            </p>
          )}

          {item.dietary_labels && item.dietary_labels.length > 0 && (
            <div className="flex flex-wrap gap-1 mt-2">
              {item.dietary_labels.map((d) => (
                <span
                  key={d}
                  className="inline-block text-[10px] font-medium px-1.5 py-0.5 rounded bg-zinc-100 text-zinc-700 capitalize"
                >
                  {d}
                </span>
              ))}
            </div>
          )}
        </div>

        {showAvailability && !isAvailable && (
          <div className="mt-3 pt-2 border-t border-[var(--mm-color-border-subtle,#F4F4F5)] flex items-center justify-between">
            <span className="text-xs font-semibold text-rose-600">
              {isSoldOut ? "Currently Sold Out" : "Unavailable Today"}
            </span>
          </div>
        )}
      </div>
    </article>
  );
}
