import {
  PublishRequest,
  PublishResponse,
  PublicationSummary,
  RollbackRequest,
  ValidationReport,
} from "../types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export async function validateMenuDraft(menuId: string, draftRevision: number = 1): Promise<ValidationReport> {
  const res = await fetch(`${API_BASE}/menus/${menuId}/validate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ draft_revision: draftRevision }),
  });
  if (!res.ok) {
    throw new Error(`Validation request failed with status ${res.status}`);
  }
  return res.json();
}

export async function getPublicationReadiness(menuId: string): Promise<{
  menu_id: string;
  ready: boolean;
  result: string;
  errors_count: number;
  warnings_count: number;
  diagnostics: any[];
}> {
  const res = await fetch(`${API_BASE}/menus/${menuId}/publication-readiness`);
  if (!res.ok) {
    throw new Error(`Readiness check failed with status ${res.status}`);
  }
  return res.json();
}

export async function publishMenu(
  menuId: string,
  request: PublishRequest,
  idempotencyKey?: string
): Promise<PublishResponse> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    "If-Match": `"draft-revision-${request.draft_revision}"`,
  };
  if (idempotencyKey) {
    headers["Idempotency-Key"] = idempotencyKey;
  }

  const res = await fetch(`${API_BASE}/menus/${menuId}/publish`, {
    method: "POST",
    headers,
    body: JSON.stringify(request),
  });

  if (!res.ok) {
    if (res.status === 409) {
      throw new Error("Concurrency conflict: Draft has been modified by another editor");
    }
    throw new Error(`Publish failed with status ${res.status}`);
  }
  return res.json();
}

export async function listPublications(menuId: string): Promise<PublicationSummary[]> {
  const res = await fetch(`${API_BASE}/menus/${menuId}/publications`);
  if (!res.ok) {
    throw new Error(`Failed to list publications: ${res.status}`);
  }
  return res.json();
}

export async function rollbackPublication(
  menuId: string,
  publicationId: string,
  request: RollbackRequest
): Promise<{ status: string; message: string; version_number: number }> {
  const res = await fetch(`${API_BASE}/menus/${menuId}/publications/${publicationId}/rollback`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });
  if (!res.ok) {
    throw new Error(`Rollback failed with status ${res.status}`);
  }
  return res.json();
}
