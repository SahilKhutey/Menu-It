import Link from 'next/link';
import { Card, CardContent, CardHeader, CardTitle, Container, EmptyState } from '@menu-it/ui';

export default function AdminBranchesDirectoryPage() {
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
        <h1>Branch Directory</h1>
        <Link href="/">← Admin Home</Link>
      </div>
      <Card>
        <CardHeader>
          <CardTitle>Physical Locations Overview</CardTitle>
        </CardHeader>
        <CardContent>
          <EmptyState
            title="Platform Admin Authentication Required"
            description="Sign in with a Platform Administrator account to inspect branch operational statuses."
          />
        </CardContent>
      </Card>
    </Container>
  );
}
