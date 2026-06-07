import type { AuthContextPort } from '../app/auth/auth-context-port';
import { getLiveSnapshotBasePrefix } from './live-snapshot-client';
import { parseRecycliqueApiErrorBody, toRecycliqueClientFailure } from './recyclique-api-error';

/** Aligné OpenAPI `UserResponse` — champs exposés par `GET /v1/users/me`. */
export type UsersMeProfileDto = {
  readonly id: string;
  readonly username?: string | null;
  readonly first_name?: string | null;
  readonly last_name?: string | null;
  readonly email?: string | null;
  readonly phone_number?: string | null;
  readonly address?: string | null;
  readonly notes?: string | null;
  readonly skills?: string | null;
  readonly availability?: string | null;
  readonly role?: string | null;
  readonly status?: string | null;
  readonly is_active?: boolean;
  readonly site_id?: string | null;
  readonly created_at?: string;
  readonly updated_at?: string;
};

export type PutUsersMePinPayload = {
  readonly pin: string;
  readonly current_password?: string;
};

type UsersMeHttpError = {
  ok: false;
  status: number;
  detail: string;
};

type UsersMePinOk = {
  ok: true;
  message: string;
};

function authHeaders(
  auth: Pick<AuthContextPort, 'getAccessToken'>,
  extra?: Record<string, string>,
): Record<string, string> {
  const headers: Record<string, string> = { Accept: 'application/json', ...extra };
  const token = auth.getAccessToken?.();
  if (token) headers.Authorization = `Bearer ${token}`;
  return headers;
}

function parseUsersMeProfile(json: unknown): UsersMeProfileDto | null {
  if (typeof json !== 'object' || json === null) return null;
  const o = json as Record<string, unknown>;
  const id = typeof o.id === 'string' ? o.id : String(o.id ?? '');
  if (!id) return null;
  return {
    id,
    username: o.username == null ? null : String(o.username),
    first_name: o.first_name == null ? null : String(o.first_name),
    last_name: o.last_name == null ? null : String(o.last_name),
    email: o.email == null ? null : String(o.email),
    phone_number: o.phone_number == null ? null : String(o.phone_number),
    address: o.address == null ? null : String(o.address),
    notes: o.notes == null ? null : String(o.notes),
    skills: o.skills == null ? null : String(o.skills),
    availability: o.availability == null ? null : String(o.availability),
    role: o.role == null ? null : String(o.role),
    status: o.status == null ? null : String(o.status),
    is_active: o.is_active === true,
    site_id: o.site_id == null ? null : String(o.site_id),
    created_at: typeof o.created_at === 'string' ? o.created_at : undefined,
    updated_at: typeof o.updated_at === 'string' ? o.updated_at : undefined,
  };
}

/** `GET /v1/users/me` — profil complet (distinct de `fetchUsersMeForAdminDashboard` qui ne retourne que `role`). */
export async function fetchUsersMeProfile(
  auth: Pick<AuthContextPort, 'getAccessToken'>,
  signal?: AbortSignal,
): Promise<UsersMeProfileDto | null> {
  const base = getLiveSnapshotBasePrefix().replace(/\/$/, '');
  const url = `${base}/v1/users/me`;
  let res: Response;
  try {
    res = await fetch(url, { method: 'GET', credentials: 'include', headers: authHeaders(auth), signal });
  } catch {
    return null;
  }
  if (!res.ok) return null;
  let json: unknown;
  try {
    json = await res.json();
  } catch {
    return null;
  }
  return parseUsersMeProfile(json);
}

/** Mappe les `detail` API PIN en messages opérateur (français). */
export function mapUsersMePinApiDetailToFrench(detail: string, httpStatus?: number): string {
  const d = detail.trim();
  if (d.includes('Current password is required')) {
    return 'Le mot de passe du compte est requis pour modifier un PIN existant.';
  }
  if (d.includes('Current password is incorrect')) {
    return 'Le mot de passe du compte est incorrect.';
  }
  if (d.includes('PIN must be exactly 4 digits') || d.includes('exactly 4 digits')) {
    return 'Le code PIN doit comporter exactement 4 chiffres.';
  }
  if (httpStatus === 401) {
    return 'Session expirée — reconnectez-vous.';
  }
  if (httpStatus === 403) {
    return "Vous n'avez pas l'autorisation de modifier ce PIN.";
  }
  return d || 'Impossible de mettre à jour le PIN.';
}

/** `PUT /v1/users/me/pin` — définition ou modification du PIN self-service. */
export async function putUsersMePin(
  auth: Pick<AuthContextPort, 'getAccessToken'>,
  payload: PutUsersMePinPayload,
): Promise<UsersMePinOk | UsersMeHttpError> {
  const base = getLiveSnapshotBasePrefix().replace(/\/$/, '');
  const url = `${base}/v1/users/me/pin`;
  let res: Response;
  try {
    res = await fetch(url, {
      method: 'PUT',
      credentials: 'include',
      headers: authHeaders(auth, { 'Content-Type': 'application/json' }),
      body: JSON.stringify(payload),
    });
  } catch {
    return { ok: false, status: 0, detail: 'Réseau indisponible — réessayez.' };
  }
  let json: unknown = null;
  try {
    json = await res.json();
  } catch {
    json = null;
  }
  if (!res.ok) {
    const p = parseRecycliqueApiErrorBody(json, res.status, 'Impossible de mettre à jour le PIN.');
    const f = toRecycliqueClientFailure(res.status, p);
    return { ok: false, status: res.status, detail: mapUsersMePinApiDetailToFrench(f.message, res.status) };
  }
  const message =
    typeof json === 'object' && json !== null && typeof (json as { message?: unknown }).message === 'string'
      ? String((json as { message: string }).message)
      : 'PIN enregistré.';
  return { ok: true, message };
}
