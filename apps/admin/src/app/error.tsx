'use client';

import { useEffect } from 'react';

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error('Admin application rendering failed.', {
      digest: error.digest,
    });
  }, [error.digest]);

  return (
    <section role="alert" style={{ padding: 24 }}>
      <h1>Something went wrong.</h1>
      <p>We could not complete this administrative request. Please try again.</p>
      <button onClick={reset}>Try again</button>
    </section>
  );
}
