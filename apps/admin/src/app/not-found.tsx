import Link from 'next/link';

export default function NotFound() {
  return (
    <main style={{ padding: 32 }}>
      <h1>404 — Admin page not found</h1>
      <p>The administrative resource requested does not exist.</p>
      <Link href="/">Return to admin console</Link>
    </main>
  );
}
