import { describe, expect, it, vi } from 'vitest';
import { restaurantConfigApi } from '../../src/services/restaurant-config-api';

describe('restaurantConfigApi', () => {
  it('calls restaurant profile and branding endpoints', async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      headers: new Headers(),
      json: async () => ({
        success: true,
        data: { id: '1', display_name: 'Spice House', version: 2 },
      }),
    });
    vi.stubGlobal('fetch', fetchMock);

    const res = await restaurantConfigApi.updateProfile('rest-1', {
      display_name: 'Spice House',
    });
    expect(res.data?.display_name).toBe('Spice House');
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining('/api/v1/restaurants/rest-1/profile'),
      expect.objectContaining({ method: 'PATCH' }),
    );
  });

  it('calls publish endpoint', async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      headers: new Headers(),
      json: async () => ({
        success: true,
        data: { id: 'p1', status: 'published', published_revision: 1 },
      }),
    });
    vi.stubGlobal('fetch', fetchMock);

    const res = await restaurantConfigApi.publishProfile('rest-1', {
      public_slug: 'spice-house',
    });
    expect(res.data?.status).toBe('published');
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining('/api/v1/restaurants/rest-1/publish'),
      expect.objectContaining({ method: 'POST' }),
    );
  });
});
