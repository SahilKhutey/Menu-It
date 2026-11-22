import type { RenderCategory, RenderMenuItem } from "@modularmenu/contracts";

export interface NavigationItem {
  id: string;
  label: string;
  href: string;
}

export interface ComposedMenuModel {
  header: {
    restaurantName: string;
    menuTitle: string;
    description?: string | null;
  };
  navigation: NavigationItem[];
  categories: RenderCategory[];
}

export function composeMenu(
  restaurantName: string,
  menuTitle: string,
  categories: RenderCategory[],
  menuDescription?: string | null
): ComposedMenuModel {
  const visibleCategories = (categories || []).filter((cat) => Array.isArray(cat.items));

  const navigation: NavigationItem[] = visibleCategories.map((cat) => ({
    id: cat.id,
    label: cat.name,
    href: `#category-${encodeURIComponent(cat.id)}`,
  }));

  return {
    header: {
      restaurantName,
      menuTitle,
      description: menuDescription,
    },
    navigation,
    categories: visibleCategories,
  };
}
