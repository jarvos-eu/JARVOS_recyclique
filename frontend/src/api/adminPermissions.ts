/**
 * Client API admin permissions — Story 3.2, 11.6.
 * GET/POST/PUT/DELETE /v1/admin/permissions.
 */

const getBase = (): string => (import.meta.env?.VITE_API_BASE_URL as string) ?? '';

function getAuthHeaders(accessToken: string): Record<string, string> {
  return {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${accessToken}`,
  };
}

export interface AdminPermission {
  id: string;
  code: string;
  label: string | null;
  created_at: string;
  updated_at: string;
}

/** GET /v1/admin/permissions — liste. */
export async function getAdminPermissions(
  accessToken: string
): Promise<AdminPermission[]> {
  const res = await fetch(`${getBase()}/v1/admin/permissions`, {
    headers: getAuthHeaders(accessToken),
  });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    const msg = typeof data?.detail === 'string' ? data.detail : `Erreur ${res.status}`;
    throw new Error(msg);
  }
  return res.json() as Promise<AdminPermission[]>;
}

/** GET /v1/admin/permissions/{permission_id}. */
export async function getAdminPermission(
  accessToken: string,
  permissionId: string
): Promise<AdminPermission> {
  const res = await fetch(`${getBase()}/v1/admin/permissions/${permissionId}`, {
    headers: getAuthHeaders(accessToken),
  });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    const msg = typeof data?.detail === 'string' ? data.detail : `Erreur ${res.status}`;
    throw new Error(msg);
  }
  return res.json() as Promise<AdminPermission>;
}

/** POST /v1/admin/permissions — création. */
export async function createAdminPermission(
  accessToken: string,
  body: { code: string; label?: string | null }
): Promise<AdminPermission> {
  const res = await fetch(`${getBase()}/v1/admin/permissions`, {
    method: 'POST',
    headers: getAuthHeaders(accessToken),
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    const msg = typeof data?.detail === 'string' ? data.detail : `Erreur ${res.status}`;
    throw new Error(msg);
  }
  return res.json() as Promise<AdminPermission>;
}

/** PUT /v1/admin/permissions/{permission_id}. */
export async function updateAdminPermission(
  accessToken: string,
  permissionId: string,
  body: { code?: string; label?: string | null }
): Promise<AdminPermission> {
  const res = await fetch(`${getBase()}/v1/admin/permissions/${permissionId}`, {
    method: 'PUT',
    headers: getAuthHeaders(accessToken),
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    const msg = typeof data?.detail === 'string' ? data.detail : `Erreur ${res.status}`;
    throw new Error(msg);
  }
  return res.json() as Promise<AdminPermission>;
}

/** DELETE /v1/admin/permissions/{permission_id}. */
export async function deleteAdminPermission(
  accessToken: string,
  permissionId: string
): Promise<void> {
  const res = await fetch(`${getBase()}/v1/admin/permissions/${permissionId}`, {
    method: 'DELETE',
    headers: getAuthHeaders(accessToken),
  });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    const msg = typeof data?.detail === 'string' ? data.detail : `Erreur ${res.status}`;
    throw new Error(msg);
  }
}
