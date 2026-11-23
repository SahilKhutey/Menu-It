export * from "./api/client";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api/v1";

export interface ApiResponse<T> {
  status: string;
  data?: T;
  version_number?: number;
  checksum?: string;
  published_at?: string;
  message?: string;
}

export async function fetchApi<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE}${endpoint.startsWith("/") ? endpoint : `/${endpoint}`}`;
  
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };

  try {
    const res = await fetch(url, {
      ...options,
      headers,
    });

    if (!res.ok) {
      const errorBody = await res.json().catch(() => ({}));
      throw new Error(errorBody.detail || `HTTP ${res.status}: ${res.statusText}`);
    }

    return await res.json();
  } catch (err: any) {
    console.warn(`[ModularMenu API] Request to ${url} failed:`, err.message);
    throw err;
  }
}

// Public API
export async function getPublicMenu(slug: string) {
  return fetchApi<ApiResponse<any>>(`/public/restaurants/${slug}/menu`, {
    cache: "no-store",
  });
}

export function getPublicQrCodeUrl(slug: string): string {
  return `${API_BASE}/public/restaurants/${slug}/qr`;
}

// Identity & Auth
export async function loginUser(email: string, password: string) {
  return fetchApi<{ access_token: string; user_id: string; email: string; full_name: string }>(
    "/auth/login",
    {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }
  );
}

// Restaurant Operations
export async function listRestaurants(token: string) {
  return fetchApi<any[]>("/restaurants", {
    headers: { Authorization: `Bearer ${token}` },
  });
}

export async function listMenus(restaurantId: string, token: string) {
  return fetchApi<any[]>(`/restaurants/${restaurantId}/menus`, {
    headers: { Authorization: `Bearer ${token}` },
  });
}

export async function listCategories(restaurantId: string, menuId: string, token: string) {
  return fetchApi<any[]>(`/restaurants/${restaurantId}/menus/${menuId}/categories`, {
    headers: { Authorization: `Bearer ${token}` },
  });
}

export async function publishMenu(restaurantId: string, menuId: string, token: string) {
  return fetchApi<{ status: string; version_number: number; checksum: string; public_url: string }>(
    `/restaurants/${restaurantId}/menus/${menuId}/publish`,
    {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
    }
  );
}

export async function updateDesignConfig(restaurantId: string, themeKey: string, customTokens: any, token: string) {
  return fetchApi<any>(`/restaurants/${restaurantId}/design`, {
    method: "PUT",
    headers: { Authorization: `Bearer ${token}` },
    body: JSON.stringify({
      theme_key: themeKey,
      custom_tokens: customTokens,
    }),
  });
}
