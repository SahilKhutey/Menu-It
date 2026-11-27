'use client';

import { useEffect, useState } from 'react';
import { Button, Card } from '@menu-it/ui';
import type { ServiceType } from '@menu-it/shared-types';
import { restaurantConfigApi } from '@/services/restaurant-config-api';

const SERVICE_TYPES: ServiceType[] = [
  'DINE_IN',
  'TAKEAWAY',
  'PICKUP',
  'DELIVERY',
  'CURBSIDE_PICKUP',
];

export default function RestaurantServicesSettingsPage({
  params,
}: {
  params: { restaurantId: string };
}) {
  const [enabledMap, setEnabledMap] = useState<Record<string, boolean>>({
    DINE_IN: true,
    TAKEAWAY: true,
    PICKUP: true,
    DELIVERY: false,
    CURBSIDE_PICKUP: false,
  });
  const [status, setStatus] = useState<string | null>(null);

  useEffect(() => {
    restaurantConfigApi
      .getServices(params.restaurantId)
      .then((res) => {
        if (res.data && res.data.length > 0) {
          const next: Record<string, boolean> = {};
          for (const row of res.data) {
            next[row.service_type] = row.enabled;
          }
          setEnabledMap((prev) => ({ ...prev, ...next }));
        }
      })
      .catch(() => {});
  }, [params.restaurantId]);

  const handleSave = async () => {
    setStatus(null);
    try {
      await restaurantConfigApi.updateServices(
        params.restaurantId,
        SERVICE_TYPES.map((st) => ({
          service_type: st,
          enabled: Boolean(enabledMap[st]),
          requires_customer_address: st === 'DELIVERY',
        })),
      );
      setStatus('Service modes saved.');
    } catch {
      setStatus('Failed to save service modes.');
    }
  };

  return (
    <main className="mx-auto max-w-3xl space-y-6 p-6">
      <h1 className="text-2xl font-semibold">Service Modes</h1>
      <Card className="space-y-4 p-6">
        {SERVICE_TYPES.map((st) => (
          <label key={st} className="flex items-center justify-between border-b pb-2">
            <span className="font-medium">{st.replace('_', ' ')}</span>
            <input
              type="checkbox"
              checked={Boolean(enabledMap[st])}
              onChange={(e) => setEnabledMap((prev) => ({ ...prev, [st]: e.target.checked }))}
            />
          </label>
        ))}
        {status && <p className="text-sm text-neutral-600">{status}</p>}
        <Button onClick={handleSave}>Save Service Modes</Button>
      </Card>
    </main>
  );
}
