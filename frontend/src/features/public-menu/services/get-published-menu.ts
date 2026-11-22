import type { MenuRenderInput } from "@modularmenu/contracts";

export interface GetPublishedMenuParams {
  restaurantSlug: string;
  menuSlug: string;
}

export async function getPublishedMenu({
  restaurantSlug,
  menuSlug,
}: GetPublishedMenuParams): Promise<MenuRenderInput | null> {
  const backendUrl = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
  const url = `${backendUrl}/api/v1/public/restaurants/${encodeURIComponent(
    restaurantSlug
  )}/menus/${encodeURIComponent(menuSlug)}`;

  try {
    const res = await fetch(url, {
      next: { revalidate: 60 },
      headers: {
        Accept: "application/json",
      },
    });

    if (res.status === 404) {
      return null;
    }

    if (!res.ok) {
      console.error(`[getPublishedMenu] Error fetching menu: HTTP ${res.status}`);
      return null;
    }

    const data: MenuRenderInput = await res.json();
    return data;
  } catch (err) {
    console.error("[getPublishedMenu] Failed to fetch published menu:", err);
    return null;
  }
}
