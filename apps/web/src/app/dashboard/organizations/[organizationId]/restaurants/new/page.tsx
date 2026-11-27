'use client';

import { useState, type FormEvent } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { Button, Card, CardContent, CardHeader, CardTitle, Container, Input } from '@menu-it/ui';
import { createOrgRestaurant } from '@/services/org-api';

export default function NewRestaurantPage() {
  const params = useParams<{ organizationId: string }>();
  const router = useRouter();
  const [name, setName] = useState('');
  const [slug, setSlug] = useState('');
  const [timezone, setTimezone] = useState('Asia/Kolkata');
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    try {
      await createOrgRestaurant(params.organizationId, {
        name: name.trim(),
        slug: slug.trim().toLowerCase(),
        timezone: timezone.trim(),
      });
      router.push(`/dashboard/organizations/${params.organizationId}/restaurants`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create restaurant.');
    }
  }

  return (
    <Container size="sm" style={{ padding: '40px 24px' }}>
      <Card>
        <CardHeader>
          <CardTitle>Create Restaurant</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} style={{ display: 'grid', gap: '16px' }}>
            {error && <p role="alert">{error}</p>}
            <label style={{ display: 'grid', gap: '6px' }}>
              <span>Restaurant Name</span>
              <Input
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Spice Garden"
                required
              />
            </label>
            <label style={{ display: 'grid', gap: '6px' }}>
              <span>Slug</span>
              <Input
                value={slug}
                onChange={(e) => setSlug(e.target.value)}
                placeholder="spice-garden"
                required
              />
            </label>
            <label style={{ display: 'grid', gap: '6px' }}>
              <span>IANA Time Zone</span>
              <Input value={timezone} onChange={(e) => setTimezone(e.target.value)} required />
            </label>
            <Button type="submit">Create Restaurant</Button>
          </form>
        </CardContent>
      </Card>
    </Container>
  );
}
