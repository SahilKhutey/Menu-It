'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import type { BranchDTO } from '@menu-it/shared-types';
import {
  Badge,
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  Container,
  EmptyState,
} from '@menu-it/ui';
import { listRestaurantBranches } from '@/services/org-api';

export default function RestaurantBranchesPage() {
  const params = useParams<{ organizationId: string; restaurantId: string }>();
  const [branches, setBranches] = useState<BranchDTO[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!params.organizationId || !params.restaurantId) return;
    listRestaurantBranches(params.restaurantId, params.organizationId)
      .then((res) => setBranches(res.data ?? []))
      .finally(() => setLoading(false));
  }, [params.organizationId, params.restaurantId]);

  return (
    <Container size="lg" style={{ padding: '40px 24px' }}>
      <Link href={`/dashboard/organizations/${params.organizationId}/restaurants`}>
        ← Back to Restaurants
      </Link>
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          margin: '16px 0 24px',
        }}
      >
        <h1>Branches</h1>
        <Link
          href={`/dashboard/organizations/${params.organizationId}/restaurants/${params.restaurantId}/branches/new`}
          className="primary-button"
        >
          Add Branch
        </Link>
      </div>

      {loading && <p>Loading branches...</p>}
      {!loading && branches.length === 0 && (
        <EmptyState
          title="No branches yet"
          description="Add a physical branch location for this restaurant."
        />
      )}

      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
          gap: '16px',
        }}
      >
        {branches.map((b) => (
          <Card key={b.id}>
            <CardHeader>
              <div
                style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}
              >
                <CardTitle>{b.name}</CardTitle>
                <Badge variant={b.status === 'active' ? 'primary' : 'default'}>{b.status}</Badge>
              </div>
            </CardHeader>
            <CardContent>
              <p>
                {b.city ? `${b.city}, ` : ''}
                {b.country_code}
              </p>
              <p style={{ fontSize: '13px', opacity: 0.8 }}>TZ: {b.timezone}</p>
            </CardContent>
          </Card>
        ))}
      </div>
    </Container>
  );
}
