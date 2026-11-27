'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import type { RestaurantSummary } from '@menu-it/shared-types';
import {
  Badge,
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  Container,
  EmptyState,
} from '@menu-it/ui';
import { listOrgRestaurants } from '@/services/org-api';

export default function OrganizationRestaurantsPage() {
  const params = useParams<{ organizationId: string }>();
  const [restaurants, setRestaurants] = useState<RestaurantSummary[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!params.organizationId) return;
    listOrgRestaurants(params.organizationId)
      .then((res) => setRestaurants(res.data?.items ?? []))
      .finally(() => setLoading(false));
  }, [params.organizationId]);

  return (
    <Container size="lg" style={{ padding: '40px 24px' }}>
      <Link href={`/dashboard/organizations/${params.organizationId}`}>← Back to Organization</Link>
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          margin: '16px 0 24px',
        }}
      >
        <h1>Restaurants</h1>
        <Link
          href={`/dashboard/organizations/${params.organizationId}/restaurants/new`}
          className="primary-button"
        >
          New Restaurant
        </Link>
      </div>

      {loading && <p>Loading restaurants...</p>}
      {!loading && restaurants.length === 0 && (
        <EmptyState
          title="No restaurants yet"
          description="Create your first restaurant brand under this organization."
        />
      )}

      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
          gap: '16px',
        }}
      >
        {restaurants.map((r) => (
          <Card key={r.id}>
            <CardHeader>
              <div
                style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}
              >
                <CardTitle>{r.name}</CardTitle>
                <Badge variant={r.status === 'active' ? 'primary' : 'default'}>{r.status}</Badge>
              </div>
            </CardHeader>
            <CardContent>
              <p>
                Slug: {r.slug} · TZ: {r.timezone}
              </p>
              <Link
                href={`/dashboard/organizations/${params.organizationId}/restaurants/${r.id}/branches`}
              >
                Manage Branches →
              </Link>
            </CardContent>
          </Card>
        ))}
      </div>
    </Container>
  );
}
