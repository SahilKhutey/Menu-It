export default function AdminHomePage() {
  return (
    <main className="admin-shell">
      <header className="admin-header">
        <div>
          <strong>Menu-It</strong>
          <span> / Platform Administration</span>
        </div>
        <span className="environment-label">DEVELOPMENT</span>
      </header>

      <section className="admin-content">
        <p className="eyebrow">PLATFORM CONSOLE</p>
        <h1>Administration workspace</h1>
        <p className="description">
          The Menu-It platform administration application is initialized.
        </p>

        <div className="foundation-card">
          <strong>Application status</strong>
          <span>Runtime shell initialized</span>
        </div>
      </section>
    </main>
  );
}
