'use client';

import { useEffect, useState } from 'react';
import { Button, Card, Input } from '@menu-it/ui';
import { restaurantConfigApi } from '@/services/restaurant-config-api';

export default function RestaurantOperationsSettingsPage({
  params,
}: {
  params: { restaurantId: string };
}) {
  const [prepBuffer, setPrepBuffer] = useState('15');
  const [minNotice, setMinNotice] = useState('0');
  const [maxAdvance, setMaxAdvance] = useState('7');
  const [maxConcurrent, setMaxConcurrent] = useState('');
  const [status, setStatus] = useState<string | null>(null);

  useEffect(() => {
    restaurantConfigApi
      .getOperations(params.restaurantId)
      .then((res) => {
        const d = res.data;
        if (!d) return;
        setPrepBuffer(String(d.preparation_buffer_minutes));
        setMinNotice(String(d.minimum_notice_minutes));
        setMaxAdvance(String(d.maximum_advance_days));
        setMaxConcurrent(d.max_concurrent_orders ? String(d.max_concurrent_orders) : '');
      })
      .catch(() => {});
  }, [params.restaurantId]);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setStatus(null);
    try {
      await restaurantConfigApi.updateOperations(params.restaurantId, {
        preparation_buffer_minutes: Number(prepBuffer) || 0,
        minimum_notice_minutes: Number(minNotice) || 0,
        maximum_advance_days: Number(maxAdvance) || 0,
        max_concurrent_orders: maxConcurrent ? Number(maxConcurrent) : null,
        auto_accept_orders: false,
        holiday_behavior: 'follow_exceptions',
      });
      setStatus('Operational settings saved.');
    } catch {
      setStatus('Failed to update operational settings.');
    }
  };

  return (
    <main className="mx-auto max-w-3xl space-y-6 p-6">
      <h1 className="text-2xl font-semibold">Operational Preferences</h1>
      <Card className="p-6">
        <form onSubmit={handleSave} className="space-y-4">
          <Input
            label="Preparation Buffer (minutes)"
            type="number"
            value={prepBuffer}
            onChange={(e) => setPrepBuffer(e.target.value)}
          />
          <Input
            label="Minimum Notice (minutes)"
            type="number"
            value={minNotice}
            onChange={(e) => setMinNotice(e.target.value)}
          />
          <Input
            label="Maximum Advance Window (days)"
            type="number"
            value={maxAdvance}
            onChange={(e) => setMaxAdvance(e.target.value)}
          />
          <Input
            label="Max Concurrent Orders (optional)"
            type="number"
            value={maxConcurrent}
            onChange={(e) => setMaxConcurrent(e.target.value)}
          />
          {status && <p className="text-sm text-neutral-600">{status}</p>}
          <Button type="submit">Save Operational Preferences</Button>
        </form>
      </Card>
    </main>
  );
}
