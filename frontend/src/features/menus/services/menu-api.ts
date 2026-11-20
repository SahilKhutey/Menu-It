/**
 * Menu Feature Service (ARC-03 §3.6)
 * Demonstrates feature-isolated API client usage without leaking infrastructure or transport logic.
 */
import { apiRequest } from "@/lib/api/client";

export interface MenuItem {
  id: string;
  name: string;
  description?: string | null;
  base_price: number;
  currency_code: string;
  dietary_type: string;
  is_available: boolean;
}

export interface Menu {
  id: string;
  name: string;
  slug: string;
  description?: string | null;
  menu_type: string;
  items?: MenuItem[];
}

export interface CreateMenuInput {
  name: string;
  slug: string;
  description?: string;
  menu_type?: string;
}

export const menuService = {
  list: (restaurantId: string, token?: string) =>
    apiRequest<Menu[]>(`/restaurants/${restaurantId}/menus`, {
      token,
    }),

  create: (restaurantId: string, data: CreateMenuInput, token?: string) =>
    apiRequest<Menu>(`/restaurants/${restaurantId}/menus`, {
      method: "POST",
      body: JSON.stringify(data),
      token,
    }),

  publish: (restaurantId: string, menuId: string, token?: string) =>
    apiRequest<{ status: string; version_number: number; checksum: string }>(
      `/restaurants/${restaurantId}/menus/${menuId}/publish`,
      {
        method: "POST",
        token,
      }
    ),
};
