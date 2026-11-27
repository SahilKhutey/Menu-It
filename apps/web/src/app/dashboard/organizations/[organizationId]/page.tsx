'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import type { OrganizationDTO } from '@menu-it/shared-types';
import { Badge, Card, CardContent, CardHeader, CardTitle, Container } from '@menu-it/ui';
import { getOrganization } from '@/services/org-api';

export default function OrganizationDashboardPage() {
  const params = useParams<{ organizationId: string }>();
  const [org, setOrg] = useState<OrganizationDTO | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!params.organizationId) return;
    getOrganization(params.organizationId)
      .then((res) => setOrg(res.data))
      .catch((err) =>
        setError(err instanceof Error ? err.message : 'Unable to load organization.'),
      );
  }, [params.organizationId]);

  return (
    <Container size="lg" style={{ padding: '40px 24px' }}>
      {error && <p role="alert">{error}</p>}
      {org && (
        <>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '24px' }}>
            <h1>{org.name}</h1>
            <Badge variant="primary">{org.status}</Badge>
          </div>
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
              gap: '16px',
            }}
          >
            <Card>
              <CardHeader>
                <CardTitle>Restaurants</CardTitle>
              </CardHeader>
              <CardContent>
                <p>Manage restaurant brands and physical branches.</p>
                <Link href={`/dashboard/organizations/${org.id}/restaurants`}>
                  Manage Restaurants →
                </Link>
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle>Team & Invitations</CardTitle>
              </CardHeader>
              <CardContent>
                <p>Manage organization members, roles, and pending invitations.</p>
                <Link href={`/dashboard/organizations/${org.id}/members`}>Manage Members →</Link>
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle>Profile & Settings</CardTitle>
              </CardHeader>
              <CardContent>
                <p>Update business contact info, currency ({org.currency_code}), and time zone.</p>
                <Link href={`/dashboard/organizations/${org.id}/settings`}>
                  Organization Settings →
                </Link>
              </CardContent>
            </Card>
          </div>
        </>
      )}
    </Container>
  );
}
