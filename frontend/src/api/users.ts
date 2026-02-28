/**
 * Client API users/me — Story 11.1 (profil).
 * GET/PUT /v1/users/me, PUT /v1/users/me/password, PUT /v1/users/me/pin.
 */

const getBase = (): string =>
  (import.meta.env?.VITE_API_BASE_URL as string) ?? '';

function authHeaders(accessToken: string): Record<string, string> {
  return {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${accessToken}`,
  };
}

export interface UserMe {
  id: string;
  username: string;
  email: string;
  first_name: string | null;
  last_name: string | null;
  role: string;
  status: string;
  site_id: string | null;
  created_at: string;
  updated_at: string;
}

export async function getMe(accessToken: string): Promise<UserMe> {
  const base = getBase();
  const res = await fetch(`${base}/v1/users/me`, {
    headers: authHeaders(accessToken),
  });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    const message = typeof data?.detail === 'string' ? data.detail : 'Erreur chargement profil';
    throw new Error(message);
  }
  return res.json() as Promise<UserMe>;
}

export async function putMe(
  accessToken: string,
  body: { first_name?: string | null; last_name?: string | null; email?: string | null }
): Promise<UserMe> {
  const base = getBase();
  const res = await fetch(`${base}/v1/users/me`, {
    method: 'PUT',
    headers: authHeaders(accessToken),
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    const message = typeof data?.detail === 'string' ? data.detail : 'Erreur mise à jour profil';
    throw new Error(message);
  }
  return res.json() as Promise<UserMe>;
}

export async function putMePassword(
  accessToken: string,
  current_password: string,
  new_password: string
): Promise<void> {
  const base = getBase();
  const res = await fetch(`${base}/v1/users/me/password`, {
    method: 'PUT',
    headers: authHeaders(accessToken),
    body: JSON.stringify({ current_password, new_password }),
  });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    const message = typeof data?.detail === 'string' ? data.detail : 'Erreur changement mot de passe';
    throw new Error(message);
  }
}

export async function putMePin(accessToken: string, new_pin: string): Promise<void> {
  const base = getBase();
  const res = await fetch(`${base}/v1/users/me/pin`, {
    method: 'PUT',
    headers: authHeaders(accessToken),
    body: JSON.stringify({ new_pin }),
  });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    const message = typeof data?.detail === 'string' ? data.detail : 'Erreur mise à jour PIN';
    throw new Error(message);
  }
}
