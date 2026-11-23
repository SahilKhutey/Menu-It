import Link from 'next/link';

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
          <span className="eyebrow">MENU-IT PLATFORM</span>
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

      <footer className="app-footer">
        <span>Menu-It</span>
        <span>© {new Date().getFullYear()} Menu-It</span>
      </footer>
    </div>
  );
}
