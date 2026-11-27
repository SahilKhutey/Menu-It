'use client';

import { useEffect, useState } from 'react';
import { Button, Card } from '@menu-it/ui';
import { restaurantConfigApi } from '@/services/restaurant-config-api';

const WEEKDAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

export default function RestaurantHoursSettingsPage({
  params,
}: {
  params: { restaurantId: string };
}) {
  const [closedDays, setClosedDays] = useState<Record<number, boolean>>({ 6: true });
  const [status, setStatus] = useState<string | null>(null);

  useEffect(() => {
    restaurantConfigApi
      .getHours(params.restaurantId)
      .then((res) => {
        if (!res.data) return;
        const next: Record<number, boolean> = {};
        for (const row of res.data) {
          if (row.is_closed) next[row.day_of_week] = true;
        }
        if (Object.keys(next).length > 0) setClosedDays(next);
      })
      .catch(() => {});
  }, [params.restaurantId]);

  const handleSave = async () => {
    setStatus(null);
    try {
      await restaurantConfigApi.replaceHours(
        params.restaurantId,
        WEEKDAYS.map((_, idx) => ({
          day_of_week: idx,
          is_closed: Boolean(closedDays[idx]),
          intervals: closedDays[idx]
            ? []
            : [{ opens_at: '09:00:00', closes_at: '22:00:00', closes_next_day: false }],
        })),
      );
      setStatus('Weekly schedule saved.');
    } catch {
      setStatus('Failed to save weekly schedule.');
    }
  };

  return (
    <main className="mx-auto max-w-3xl space-y-6 p-6">
      <h1 className="text-2xl font-semibold">Business Hours</h1>
      <Card className="space-y-4 p-6">
        {WEEKDAYS.map((day, idx) => (
          <div key={day} className="flex items-center justify-between border-b pb-2">
            <span className="font-medium">{day}</span>
            <label className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={Boolean(closedDays[idx])}
                onChange={(e) => setClosedDays((prev) => ({ ...prev, [idx]: e.target.checked }))}
              />
              Closed
            </label>
          </div>
        ))}
        {status && <p className="text-sm text-neutral-600">{status}</p>}
        <Button onClick={handleSave}>Save Weekly Hours</Button>
      </Card>
    </main>
  );
}
