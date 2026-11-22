"use client";

import React from "react";
import type { NavigationItem } from "../../../lib/rendering";

interface CategoryNavigationProps {
  items: NavigationItem[];
  activeId?: string;
  onSelect?: (id: string) => void;
}

export function CategoryNavigation({ items, activeId, onSelect }: CategoryNavigationProps) {
  if (!items || items.length === 0) return null;

  return (
    <nav
      className="category-navigation sticky top-0 z-30 bg-[var(--mm-color-surface-default,#FFFFFF)]/95 backdrop-blur-md border-b border-[var(--mm-color-border-subtle,#F4F4F5)] py-2.5 px-4 shadow-sm"
      aria-label="Menu categories"
    >
      <div className="max-w-4xl mx-auto flex items-center gap-2 overflow-x-auto no-scrollbar scroll-smooth">
        {items.map((item) => {
          const isActive = activeId === item.id;
          return (
            <a
              key={item.id}
              href={item.href}
              onClick={(e) => {
                if (onSelect) {
                  e.preventDefault();
                  onSelect(item.id);
                  const el = document.querySelector(item.href);
                  if (el) el.scrollIntoView({ behavior: "smooth" });
                }
              }}
              className={`whitespace-nowrap px-3.5 py-1.5 rounded-full text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-[var(--mm-color-brand-primary,#18181B)] ${
                isActive
                  ? "bg-[var(--mm-color-brand-primary,#18181B)] text-white shadow-sm"
                  : "bg-zinc-100 text-zinc-700 hover:bg-zinc-200"
              }`}
            >
              {item.label}
            </a>
          );
        })}
      </div>
    </nav>
  );
}
