'use client';

import { useState, type FormEvent } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { Button, Card, CardContent, CardHeader, CardTitle, Container, Input } from '@menu-it/ui';
import { createRestaurantBranch } from '@/services/org-api';

export default function NewBranchPage() {
  const params = useParams<{ organizationId: string; restaurantId: string }>();
  const router = useRouter();
  const [name, setName] = useState('');
  const [slug, setSlug] = useState('');
  const [city, setCity] = useState('');
  const [countryCode, setCountryCode] = useState('IN');
  const [timezone, setTimezone] = useState('Asia/Kolkata');
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    try {
      await createRestaurantBranch(params.restaurantId, params.organizationId, {
        name: name.trim(),
        slug: slug.trim().toLowerCase(),
        city: city.trim() || null,
        country_code: countryCode.trim().toUpperCase(),
        timezone: timezone.trim(),
      });
      router.push(
        `/dashboard/organizations/${params.organizationId}/restaurants/${params.restaurantId}/branches`,
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create branch.');
    }
  }

  return (
    <Container size="sm" style={{ padding: '40px 24px' }}>
      <Card>
        <CardHeader>
          <CardTitle>Add Physical Branch</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} style={{ display: 'grid', gap: '16px' }}>
            {error && <p role="alert">{error}</p>}
            <label style={{ display: 'grid', gap: '6px' }}>
              <span>Branch Name</span>
              <Input
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Spice Garden — Bilaspur"
                required
              />
            </label>
            <label style={{ display: 'grid', gap: '6px' }}>
              <span>Slug</span>
              <Input
                value={slug}
                onChange={(e) => setSlug(e.target.value)}
                placeholder="bilaspur"
                required
              />
            </label>
            <label style={{ display: 'grid', gap: '6px' }}>
              <span>City</span>
              <Input
                value={city}
                onChange={(e) => setCity(e.target.value)}
                placeholder="Bilaspur"
              />
            </label>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
              <label style={{ display: 'grid', gap: '6px' }}>
                <span>Country (ISO-2)</span>
                <Input
                  value={countryCode}
                  onChange={(e) => setCountryCode(e.target.value)}
                  maxLength={2}
                  required
                />
              </label>
              <label style={{ display: 'grid', gap: '6px' }}>
                <span>IANA Time Zone</span>
                <Input value={timezone} onChange={(e) => setTimezone(e.target.value)} required />
              </label>
            </div>
            <Button type="submit">Create Branch</Button>
          </form>
        </CardContent>
      </Card>
    </Container>
  );
}
