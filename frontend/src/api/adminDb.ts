/**
 * Client API admin BDD — Story 8.5.
 * POST /v1/admin/db/export, purge-transactions, import.
 */

const getBase = (): string =>
  (import.meta.env?.VITE_API_BASE_URL as string) ?? '';

function getAuthHeaders(accessToken: string): Record<string, string> {
  return {
    Authorization: `Bearer ${accessToken}`,
  };
}

function getAuthHeadersJson(accessToken: string): Record<string, string> {
  return {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${accessToken}`,
  };
}

export interface DbPurgeResponse {
  message: string;
  deleted_count: number;
}

export async function postAdminDbExport(accessToken: string): Promise<void> {
  const res = await fetch(`${getBase()}/v1/admin/db/export`, {
    method: 'POST',
    headers: getAuthHeaders(accessToken),
  });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    const msg = typeof data?.detail === 'string' ? data.detail : `Erreur ${res.status}`;
    throw new Error(msg);
  }
  const blob = await res.blob();
  const disposition = res.headers.get('Content-Disposition');
  const match = disposition?.match(/filename="?([^";]+)"?/);
  const name = match?.[1] ?? 'recyclique-export.sql';
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = name;
  a.click();
  URL.revokeObjectURL(a.href);
}

export async function postAdminDbPurgeTransactions(
  accessToken: string
): Promise<DbPurgeResponse> {
  const res = await fetch(`${getBase()}/v1/admin/db/purge-transactions`, {
    method: 'POST',
    headers: getAuthHeadersJson(accessToken),
    body: JSON.stringify({}),
  });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    const msg = typeof data?.detail === 'string' ? data.detail : `Erreur ${res.status}`;
    throw new Error(msg);
  }
  return res.json() as Promise<DbPurgeResponse>;
}

export interface DbImportResponse {
  ok: boolean;
  message?: string;
  filename?: string;
  detail?: string;
}

export async function postAdminDbImport(
  accessToken: string,
  file: File
): Promise<DbImportResponse> {
  const form = new FormData();
  form.append('file', file);
  const res = await fetch(`${getBase()}/v1/admin/db/import`, {
    method: 'POST',
    headers: getAuthHeaders(accessToken),
    body: form,
  });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    const msg = typeof data?.detail === 'string' ? data.detail : `Erreur ${res.status}`;
    throw new Error(msg);
  }
  return res.json() as Promise<DbImportResponse>;
}
