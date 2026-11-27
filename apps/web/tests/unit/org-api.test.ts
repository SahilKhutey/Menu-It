import { describe, it, expect, vi, beforeEach } from 'vitest';
import {
  createOrganization,
  createOrgRestaurant,
  createRestaurantBranch,
} from '../../src/services/org-api';

describe('FCD-14 Organization, Restaurant & Branch API Client', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('calls POST /organizations with canonical envelope', async () => {
    const mockOrg = {
      id: '00000000-0000-0000-0000-000000000001',
      name: 'ABC Hospitality',
      slug: 'abc-hospitality',
      status: 'active',
      country_code: 'IN',
      currency_code: 'INR',
      timezone: 'Asia/Kolkata',
    };
    const fetchSpy = vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(JSON.stringify({ success: true, data: mockOrg, error: null, meta: {} }), {
        status: 201,
        headers: { 'Content-Type': 'application/json' },
      }),
    );

    const res = await createOrganization({
      name: 'ABC Hospitality',
      slug: 'abc-hospitality',
      currency_code: 'INR',
      timezone: 'Asia/Kolkata',
      country_code: 'IN',
    });
    expect(res.data?.slug).toBe('abc-hospitality');
    expect(fetchSpy).toHaveBeenCalledTimes(1);
  });

  it('calls POST /organizations/:id/restaurants and POST /restaurants/:id/branches', async () => {
    const fetchSpy = vi.spyOn(globalThis, 'fetch').mockImplementation(async () =>
      new Response(JSON.stringify({ success: true, data: { id: '123' }, error: null, meta: {} }), {
        status: 201,
        headers: { 'Content-Type': 'application/json' },
      }),
    );

    await createOrgRestaurant('org-1', {
      name: 'Spice Garden',
      slug: 'spice-garden',
      timezone: 'Asia/Kolkata',
    });
    await createRestaurantBranch('rest-1', 'org-1', {
      name: 'Bilaspur',
      slug: 'bilaspur',
      timezone: 'Asia/Kolkata',
      country_code: 'IN',
    });
    expect(fetchSpy).toHaveBeenCalledTimes(2);
  });
});
