'use client';

import { useEffect, useState } from 'react';
import { Button, Card, Input } from '@menu-it/ui';
import { restaurantConfigApi } from '@/services/restaurant-config-api';

export default function RestaurantBrandingSettingsPage({
  params,
}: {
  params: { restaurantId: string };
}) {
  const [primaryColor, setPrimaryColor] = useState('#111827');
  const [secondaryColor, setSecondaryColor] = useState('#F97316');
  const [fontFamily, setFontFamily] = useState('Inter');
  const [revision, setRevision] = useState<number | undefined>(undefined);
  const [status, setStatus] = useState<string | null>(null);

  useEffect(() => {
    restaurantConfigApi
      .getBranding(params.restaurantId)
      .then((res) => {
        const d = res.data;
        if (!d) return;
        if (d.primary_color) setPrimaryColor(d.primary_color);
        if (d.secondary_color) setSecondaryColor(d.secondary_color);
        if (d.font_family) setFontFamily(d.font_family);
        setRevision(d.revision);
      })
      .catch(() => setStatus('Unable to load branding settings.'));
  }, [params.restaurantId]);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setStatus(null);
    try {
      const updated = await restaurantConfigApi.updateBranding(params.restaurantId, {
        primary_color: primaryColor,
        secondary_color: secondaryColor,
        font_family: fontFamily,
        expected_revision: revision,
      });
      if (updated.data) setRevision(updated.data.revision);
      setStatus('Branding updated.');
    } catch {
      setStatus('Failed to update branding.');
    }
  };

  return (
    <main className="mx-auto max-w-3xl space-y-6 p-6">
      <h1 className="text-2xl font-semibold">Branding & Theme</h1>
      <Card className="p-6">
        <form onSubmit={handleSave} className="space-y-4">
          <Input
            label="Primary Hex Color"
            value={primaryColor}
            onChange={(e) => setPrimaryColor(e.target.value)}
          />
          <Input
            label="Secondary Hex Color"
            value={secondaryColor}
            onChange={(e) => setSecondaryColor(e.target.value)}
          />
          <Input
            label="Font Family"
            value={fontFamily}
            onChange={(e) => setFontFamily(e.target.value)}
          />
          <div className="rounded-md border p-4" style={{ borderColor: primaryColor, fontFamily }}>
            <p className="font-semibold" style={{ color: primaryColor }}>
              Brand Preview Header
            </p>
            <p className="text-sm" style={{ color: secondaryColor }}>
              Accent & Secondary Color Sample
            </p>
          </div>
          {status && <p className="text-sm text-neutral-600">{status}</p>}
          <Button type="submit">Save Branding</Button>
        </form>
      </Card>
    </main>
  );
}
