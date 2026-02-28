/**
 * Client API admin groups — Story 3.2, 11.6.
 * GET/POST/PUT/DELETE /v1/admin/groups, POST/DELETE groups/{id}/permissions, groups/{id}/users.
 */

const getBase = (): string => (import.meta.env?.VITE_API_BASE_URL as string) ?? '';

function getAuthHeaders(accessToken: string): Record<string, string> {
  return {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${accessToken}`,
  };
}

export interface AdminGroup {
  id: string;
  name: string;
  description: string | null;
  created_at: string;
  updated_at: string;
}

export interface AdminGroupDetail extends AdminGroup {
  permission_ids: string[];
  user_ids: string[];
}

/** GET /v1/admin/groups — liste des groupes. */
export async function getAdminGroups(accessToken: string): Promise<AdminGroup[]> {
  const res = await fetch(`${getBase()}/v1/admin/groups`, {
    headers: getAuthHeaders(accessToken),
  });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    const msg = typeof data?.detail === 'string' ? data.detail : `Erreur ${res.status}`;
    throw new Error(msg);
  }
  return res.json() as Promise<AdminGroup[]>;
}

/** GET /v1/admin/groups/{group_id} — détail (permission_ids, user_ids). */
export async function getAdminGroup(
  accessToken: string,
  groupId: string
): Promise<AdminGroupDetail> {
  const res = await fetch(`${getBase()}/v1/admin/groups/${groupId}`, {
    headers: getAuthHeaders(accessToken),
  });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    const msg = typeof data?.detail === 'string' ? data.detail : `Erreur ${res.status}`;
    throw new Error(msg);
  }
  return res.json() as Promise<AdminGroupDetail>;
}

/** POST /v1/admin/groups — création. */
export async function createAdminGroup(
  accessToken: string,
  body: { name: string; description?: string | null }
): Promise<AdminGroup> {
  const res = await fetch(`${getBase()}/v1/admin/groups`, {
    method: 'POST',
    headers: getAuthHeaders(accessToken),
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    const msg = typeof data?.detail === 'string' ? data.detail : `Erreur ${res.status}`;
    throw new Error(msg);
  }
  return res.json() as Promise<AdminGroup>;
}

/** PUT /v1/admin/groups/{group_id} — mise à jour. */
export async function updateAdminGroup(
  accessToken: string,
  groupId: string,
  body: { name?: string; description?: string | null }
): Promise<AdminGroup> {
  const res = await fetch(`${getBase()}/v1/admin/groups/${groupId}`, {
    method: 'PUT',
    headers: getAuthHeaders(accessToken),
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    const msg = typeof data?.detail === 'string' ? data.detail : `Erreur ${res.status}`;
    throw new Error(msg);
  }
  return res.json() as Promise<AdminGroup>;
}

/** DELETE /v1/admin/groups/{group_id}. */
export async function deleteAdminGroup(
  accessToken: string,
  groupId: string
): Promise<void> {
  const res = await fetch(`${getBase()}/v1/admin/groups/${groupId}`, {
    method: 'DELETE',
    headers: getAuthHeaders(accessToken),
  });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    const msg = typeof data?.detail === 'string' ? data.detail : `Erreur ${res.status}`;
    throw new Error(msg);
  }
}

/** POST /v1/admin/groups/{group_id}/permissions — ajouter permission(s). */
export async function addGroupPermissions(
  accessToken: string,
  groupId: string,
  body: { permission_id?: string; permission_ids?: string[] }
): Promise<void> {
  const res = await fetch(`${getBase()}/v1/admin/groups/${groupId}/permissions`, {
    method: 'POST',
    headers: getAuthHeaders(accessToken),
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    const msg = typeof data?.detail === 'string' ? data.detail : `Erreur ${res.status}`;
    throw new Error(msg);
  }
}

/** DELETE /v1/admin/groups/{group_id}/permissions/{permission_id}. */
export async function removeGroupPermission(
  accessToken: string,
  groupId: string,
  permissionId: string
): Promise<void> {
  const res = await fetch(
    `${getBase()}/v1/admin/groups/${groupId}/permissions/${permissionId}`,
    { method: 'DELETE', headers: getAuthHeaders(accessToken) }
  );
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    const msg = typeof data?.detail === 'string' ? data.detail : `Erreur ${res.status}`;
    throw new Error(msg);
  }
}

/** POST /v1/admin/groups/{group_id}/users — ajouter utilisateur(s). */
export async function addGroupUsers(
  accessToken: string,
  groupId: string,
  body: { user_id?: string; user_ids?: string[] }
): Promise<void> {
  const res = await fetch(`${getBase()}/v1/admin/groups/${groupId}/users`, {
    method: 'POST',
    headers: getAuthHeaders(accessToken),
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    const msg = typeof data?.detail === 'string' ? data.detail : `Erreur ${res.status}`;
    throw new Error(msg);
  }
}

/** DELETE /v1/admin/groups/{group_id}/users/{user_id}. */
export async function removeGroupUser(
  accessToken: string,
  groupId: string,
  userId: string
): Promise<void> {
  const res = await fetch(
    `${getBase()}/v1/admin/groups/${groupId}/users/${userId}`,
    { method: 'DELETE', headers: getAuthHeaders(accessToken) }
  );
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    const msg = typeof data?.detail === 'string' ? data.detail : `Erreur ${res.status}`;
    throw new Error(msg);
  }
}
