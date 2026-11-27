import Link from 'next/link';
import { Card, CardContent, CardHeader, CardTitle, Container, EmptyState } from '@menu-it/ui';

export default function AdminRestaurantsDirectoryPage() {
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
        <h1>Restaurant Directory</h1>
        <Link href="/">← Admin Home</Link>
      </div>
      <Card>
        <CardHeader>
          <CardTitle>Registered Restaurant Brands</CardTitle>
        </CardHeader>
        <CardContent>
          <EmptyState
            title="Platform Admin Authentication Required"
            description="Sign in with a Platform Administrator account to view cross-tenant restaurant directories."
          />
        </CardContent>
      </Card>
    </Container>
  );
}
