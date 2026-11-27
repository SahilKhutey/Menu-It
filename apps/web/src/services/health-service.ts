const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:8000/api/v1';

export interface BackendHealth {
  status: string;
  application: string;
  version: string;
}

export async function checkBackendHealth(): Promise<BackendHealth> {
  const response = await fetch(`${API_BASE_URL}/health`, {
    cache: 'no-store',
  });

  if (!response.ok) {
    throw new Error('Backend health check failed.');
  }

  return response.json() as Promise<BackendHealth>;
}
