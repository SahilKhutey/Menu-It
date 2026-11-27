'use client';

import { useEffect, useState } from 'react';
import { Button, Card, Input } from '@menu-it/ui';
import { restaurantConfigApi } from '@/services/restaurant-config-api';

export default function RestaurantProfileSettingsPage({
  params,
}: {
  params: { restaurantId: string };
}) {
  const [displayName, setDisplayName] = useState('');
  const [cuisineType, setCuisineType] = useState('');
  const [shortDescription, setShortDescription] = useState('');
  const [publicEmail, setPublicEmail] = useState('');
  const [publicPhone, setPublicPhone] = useState('');
  const [version, setVersion] = useState<number | undefined>(undefined);
  const [status, setStatus] = useState<string | null>(null);

  useEffect(() => {
    restaurantConfigApi
      .getProfile(params.restaurantId)
      .then((res) => {
        const d = res.data;
        if (!d) return;
        setDisplayName(d.display_name);
        setCuisineType(d.cuisine_type ?? '');
        setShortDescription(d.short_description ?? '');
        setPublicEmail(d.public_email ?? '');
        setPublicPhone(d.public_phone ?? '');
        setVersion(d.version);
      })
      .catch(() => setStatus('Unable to load restaurant profile.'));
  }, [params.restaurantId]);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setStatus(null);
    try {
      const updated = await restaurantConfigApi.updateProfile(params.restaurantId, {
        display_name: displayName,
        cuisine_type: cuisineType || null,
        short_description: shortDescription || null,
        public_email: publicEmail || null,
        public_phone: publicPhone || null,
        expected_version: version,
      });
      if (updated.data) setVersion(updated.data.version);
      setStatus('Profile saved.');
    } catch {
      setStatus('Failed to save profile.');
    }
  };

  return (
    <main className="mx-auto max-w-3xl space-y-6 p-6">
      <h1 className="text-2xl font-semibold">Restaurant Profile</h1>
      <Card className="p-6">
        <form onSubmit={handleSave} className="space-y-4">
          <Input
            label="Display Name"
            value={displayName}
            onChange={(e) => setDisplayName(e.target.value)}
            required
          />
          <Input
            label="Cuisine Type"
            value={cuisineType}
            onChange={(e) => setCuisineType(e.target.value)}
          />
          <Input
            label="Short Description"
            value={shortDescription}
            onChange={(e) => setShortDescription(e.target.value)}
          />
          <Input
            label="Public Email"
            type="email"
            value={publicEmail}
            onChange={(e) => setPublicEmail(e.target.value)}
          />
          <Input
            label="Public Phone"
            value={publicPhone}
            onChange={(e) => setPublicPhone(e.target.value)}
          />
          {status && <p className="text-sm text-neutral-600">{status}</p>}
          <Button type="submit">Save Profile</Button>
        </form>
      </Card>
    </main>
  );
}
