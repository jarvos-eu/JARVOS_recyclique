/**
 * Story 8.6 — GET /v1/admin/paheko-compta-url (URL admin Paheko pour compta).
 */

const getBase = (): string =>
  (import.meta.env?.VITE_API_BASE_URL as string) ?? '';

function getAuthHeaders(accessToken: string): Record<string, string> {
  return {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${accessToken}`,
  };
}

export interface PahekoComptaUrlResponse {
  url: string;
}

/** GET /v1/admin/paheko-compta-url — URL pour ouvrir l'admin compta Paheko. 404 si non configuré. */
export async function getPahekoComptaUrl(
  accessToken: string
): Promise<PahekoComptaUrlResponse> {
  const res = await fetch(`${getBase()}/v1/admin/paheko-compta-url`, {
    headers: getAuthHeaders(accessToken),
  });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    const msg = typeof data?.detail === 'string' ? data.detail : `Erreur ${res.status}`;
    throw new Error(msg);
  }
  return res.json() as Promise<PahekoComptaUrlResponse>;
}
