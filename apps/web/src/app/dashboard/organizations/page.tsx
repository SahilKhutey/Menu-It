'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import type { OrganizationDTO } from '@menu-it/shared-types';
import {
  Badge,
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  Container,
  EmptyState,
} from '@menu-it/ui';
import { listOrganizations } from '@/services/org-api';

export default function OrganizationsListPage() {
  const [orgs, setOrgs] = useState<OrganizationDTO[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    listOrganizations()
      .then((res) => setOrgs(res.data ?? []))
      .catch((err) =>
        setError(err instanceof Error ? err.message : 'Failed to load organizations.'),
      )
      .finally(() => setLoading(false));
  }, []);

  return (
    <Container size="lg" style={{ padding: '40px 24px' }}>
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '24px',
        }}
      >
        <h1>Organizations</h1>
        <Link href="/onboarding/organization" className="primary-button">
          New Organization
        </Link>
      </div>

      {loading && <p>Loading organizations...</p>}
      {error && <p role="alert">{error}</p>}
      {!loading && !error && orgs.length === 0 && (
        <EmptyState
          title="No organizations yet"
          description="Create your first hospitality organization to manage restaurants and branches."
        />
      )}

      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
          gap: '16px',
        }}
      >
        {orgs.map((org) => (
          <Card key={org.id}>
            <CardHeader>
              <div
                style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}
              >
                <CardTitle>{org.name}</CardTitle>
                <Badge variant={org.status === 'active' ? 'primary' : 'default'}>
                  {org.status}
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              <p style={{ fontSize: '14px', opacity: 0.8 }}>Slug: {org.slug}</p>
              <p style={{ fontSize: '14px', opacity: 0.8 }}>
                {org.country_code} · {org.currency_code} · {org.timezone}
              </p>
              <div style={{ marginTop: '12px' }}>
                <Link href={`/dashboard/organizations/${org.id}`}>Open Workspace →</Link>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </Container>
  );
}
