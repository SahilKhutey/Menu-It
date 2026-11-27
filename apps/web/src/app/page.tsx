import Link from 'next/link';
import { Badge, Card, CardHeader, CardTitle, CardContent, Container } from '@menu-it/ui';

export default function HomePage() {
  return (
    <div className="app-shell">
      <header className="app-header">
        <Link href="/" className="brand">
          Menu-It
        </Link>
        <nav className="desktop-navigation" aria-label="Main navigation">
          <Link href="/">Home</Link>
          <Link href="/restaurants">Restaurants</Link>
          <Link href="/about">About</Link>
        </nav>
        <Link href="/login" className="header-action">
          Sign in
        </Link>
      </header>

      <section className="hero">
        <div className="hero-content">
          <Badge variant="primary" style={{ marginBottom: '16px' }}>
            MENU-IT PLATFORM
          </Badge>
          <h1>
            A better way to <br /> experience dining.
          </h1>
          <p>Discover a modern restaurant experience powered by the Menu-It platform.</p>
          <div className="hero-actions">
            <Link href="/restaurants" className="primary-button">
              Explore restaurants
            </Link>
            <Link href="/about" className="secondary-button">
              Learn more
            </Link>
          </div>
        </div>
      </section>

      <Container size="lg" style={{ padding: '48px 24px' }}>
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
            gap: '24px',
          }}
        >
          <Card>
            <CardHeader>
              <CardTitle>Digital QR Menus</CardTitle>
            </CardHeader>
            <CardContent>
              Instant, contactless digital ordering experience with full multi-lingual and theming
              support.
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>Multi-Tenant Operations</CardTitle>
            </CardHeader>
            <CardContent>
              Dedicated tenant isolation, localized menus, and live order synchronization across
              branches.
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>Accessible & Responsive</CardTitle>
            </CardHeader>
            <CardContent>
              WCAG 2.2 AA compliant typography, high-contrast tokens, and fluid layouts for all
              devices.
            </CardContent>
          </Card>
        </div>
      </Container>

      <footer className="app-footer">
        <span>Menu-It</span>
        <span>© {new Date().getFullYear()} Menu-It</span>
      </footer>
    </div>
  );
}
