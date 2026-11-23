/**
 * ModularMenu — TanStack Query Key Factories (ARC-07 §13.5).
 * Encapsulates tenant namespacing to prevent cross-tenant cache contamination.
 */

export const queryKeys = {
  auth: {
    session: () => ["auth", "session"] as const,
    profile: () => ["auth", "profile"] as const,
  },
  organizations: {
    all: () => ["organizations"] as const,
    detail: (orgId: string) => ["organizations", orgId] as const,
    members: (orgId: string) => ["organizations", orgId, "members"] as const,
  },
  restaurants: {
    list: (orgId?: string) => ["restaurants", { orgId }] as const,
    detail: (restaurantId: string) => ["restaurants", restaurantId] as const,
    settings: (restaurantId: string) => ["restaurants", restaurantId, "settings"] as const,
    designConfig: (restaurantId: string) => ["restaurants", restaurantId, "design-config"] as const,
  },
  menus: {
    list: (restaurantId: string) => ["restaurants", restaurantId, "menus"] as const,
    detail: (menuId: string) => ["menus", menuId] as const,
    categories: (menuId: string) => ["menus", menuId, "categories"] as const,
    editorState: (menuId: string) => ["menus", menuId, "editor-state"] as const,
    versions: (menuId: string) => ["menus", menuId, "versions"] as const,
    publications: (menuId: string) => ["menus", menuId, "publications"] as const,
  },
  themes: {
    presets: () => ["themes", "presets"] as const,
    layouts: () => ["layouts"] as const,
    components: () => ["components"] as const,
  },
  publicMenu: {
    restaurant: (slug: string) => ["public", "restaurants", slug] as const,
    snapshot: (restaurantSlug: string, menuSlug: string) =>
      ["public", "restaurants", restaurantSlug, "menus", menuSlug] as const,
  },
};
