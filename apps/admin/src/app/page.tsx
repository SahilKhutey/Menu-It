import { Badge, Card, CardHeader, CardTitle, CardContent, Container, Stack } from '@menu-it/ui';

export default function AdminHomePage() {
  return (
    <main className="admin-shell">
      <header className="admin-header">
        <div>
          <strong>Menu-It</strong>
          <span> / Platform Administration</span>
        </div>
        <Badge variant="outline">DEVELOPMENT</Badge>
      </header>

      <Container size="md" style={{ padding: '80px 24px' }}>
        <p className="eyebrow">PLATFORM CONSOLE</p>
        <h1>Administration workspace</h1>
        <p className="description">
          The Menu-It platform administration application is initialized with full design system
          support.
        </p>

        <Stack gap="md" style={{ marginTop: '32px' }}>
          <Card>
            <CardHeader>
              <CardTitle>Application Status</CardTitle>
            </CardHeader>
            <CardContent>
              <div
                style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}
              >
                <span>Runtime Shell &amp; Design System</span>
                <Badge variant="success">Operational</Badge>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Multi-Tenant Engine</CardTitle>
            </CardHeader>
            <CardContent>
              <div
                style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}
              >
                <span>Tenant &amp; Organization Scoping</span>
                <Badge variant="primary">Active</Badge>
              </div>
            </CardContent>
          </Card>
        </Stack>
      </Container>
    </main>
  );
}
