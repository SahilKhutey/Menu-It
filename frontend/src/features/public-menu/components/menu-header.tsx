import React from "react";
import type { RenderMenuData } from "@modularmenu/contracts";

interface MenuHeaderProps {
  menu: RenderMenuData;
}

export function MenuHeader({ menu }: MenuHeaderProps) {
  return (
    <section className="menu-header max-w-4xl mx-auto px-4 pt-6 pb-2 text-center md:text-left">
      <h2 className="text-2xl md:text-3xl font-extrabold tracking-tight text-[var(--mm-color-text-primary,#09090B)] font-[var(--mm-typography-fontFamily-heading,inherit)]">
        {menu.title}
      </h2>
      {menu.description && (
        <p className="mt-1 text-sm text-[var(--mm-color-text-secondary,#71717A)] max-w-2xl">
          {menu.description}
        </p>
      )}
    </section>
  );
}
