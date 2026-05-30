import type { AuthContextPort } from '../app/auth/auth-context-port';
import { getLiveSnapshotBasePrefix } from './live-snapshot-client';
import { parseRecycliqueApiErrorBody, toRecycliqueClientFailure } from './recyclique-api-error';

/** Aligné OpenAPI `RegisteredDeviceV1*` — types générés à rafraîchir quand le pipeline regénère `recyclique-api`. */
export type RegisteredDeviceAdminRowDto = {
  device_id: string;
  device_type: 'shared_workstation';
  name: string;
  location?: string | null;
  site_id: string;
  status: string;
  revoked_at?: string | null;
  allowed_module_keys: string[];
  inactivity_timeout_seconds?: number | null;
  last_contact_at?: string | null;
  created_at?: string | null;
  updated_at?: string | null;
};

export type RegisteredDeviceAdminCreateBody = {
  name: string;
  site_id: string;
  location?: string | null;
  device_type?: 'shared_workstation';
  status?: string;
  allowed_module_keys?: string[];
  inactivity_timeout_seconds?: number;
};

export type RegisteredDeviceAdminUpdateBody = {
  name?: string;
  site_id?: string;
  location?: string | null;
  /**
   * Ne jamais passer `status: 'revoked'` — utiliser `revokeRegisteredDeviceForAdmin` (POST /revoke).
   * Le backend rejette toute tentative via 422. Invariant ADR Epic 27 / mini-ADR postes partagés.
   */
  status?: string;
  allowed_module_keys?: string[];
  inactivity_timeout_seconds?: number;
  last_contact_at?: string | null;
};

export type RegisteredDeviceRevokeBody = {
  reason?: string;
};

export type RegisteredDevicesListQuery = {
  readonly skip?: number;
  readonly limit?: number;
  readonly site_id?: string | null;
  readonly status?: string | null;
  readonly include_revoked?: boolean;
};

type RegisteredDevicesHttpError = {
  ok: false;
  status: number;
  detail: string;
  code?: string;
  retryable?: boolean;
  state?: string | null;
  correlation_id?: string;
  networkError?: boolean;
};

function rdHttpError(
  status: number,
  json: unknown,
  fallbackDetail: string,
  networkError?: boolean,
): RegisteredDevicesHttpError {
  const p = parseRecycliqueApiErrorBody(json, status, fallbackDetail);
  const f = toRecycliqueClientFailure(status, p, networkError);
  return {
    ok: false,
    status,
    detail: f.message,
    code: f.code,
    retryable: f.retryable,
    state: f.state,
    correlation_id: f.correlationId,
    networkError: f.networkError,
  };
}

function authHeaders(
  auth: Pick<AuthContextPort, 'getAccessToken'>,
  extra?: Record<string, string>,
): Record<string, string> {
  const headers: Record<string, string> = { Accept: 'application/json', ...extra };
  const token = auth.getAccessToken?.();
  if (token) headers.Authorization = `Bearer ${token}`;
  return headers;
}

function parseJsonText(text: string): unknown {
  if (!text) return null;
  try {
    return JSON.parse(text) as unknown;
  } catch {
    return null;
  }
}

function isRecord(x: unknown): x is Record<string, unknown> {
  return typeof x === 'object' && x !== null;
}

function parseDeviceRow(row: unknown): RegisteredDeviceAdminRowDto | null {
  if (!isRecord(row)) return null;
  const device_id = row.device_id;
  const device_type = row.device_type;
  const name = row.name;
  const site_id = row.site_id;
  const status = row.status;
  const allowed_module_keys = row.allowed_module_keys;
  if (typeof device_id !== 'string' || typeof name !== 'string') return null;
  if (typeof device_type !== 'string' || typeof site_id !== 'string') return null;
  if (typeof status !== 'string') return null;
  if (!Array.isArray(allowed_module_keys)) return null;
  return row as RegisteredDeviceAdminRowDto;
}

export type RegisteredDevicesListResult =
  | { ok: true; data: readonly RegisteredDeviceAdminRowDto[] }
  | RegisteredDevicesHttpError;

export type RegisteredDeviceMutationResult =
  | { ok: true; device: RegisteredDeviceAdminRowDto }
  | RegisteredDevicesHttpError;

/** GET /v1/registered-devices/ */
export async function listRegisteredDevicesForAdmin(
  auth: Pick<AuthContextPort, 'getAccessToken'>,
  query: RegisteredDevicesListQuery = {},
  signal?: AbortSignal,
): Promise<RegisteredDevicesListResult> {
  const base = getLiveSnapshotBasePrefix();
  const sp = new URLSearchParams();
  if (typeof query.skip === 'number') sp.set('skip', String(query.skip));
  if (typeof query.limit === 'number') sp.set('limit', String(query.limit));
  if (query.site_id && query.site_id.trim() !== '') sp.set('site_id', query.site_id.trim());
  if (query.status && query.status.trim() !== '') sp.set('status', query.status.trim());
  if (query.include_revoked === true) sp.set('include_revoked', 'true');
  const qs = sp.toString();
  const url = `${base}/v1/registered-devices/${qs ? `?${qs}` : ''}`;
  let res: Response;
  try {
    res = await fetch(url, { method: 'GET', credentials: 'include', headers: authHeaders(auth), signal });
  } catch (e) {
    const msg = e instanceof Error ? e.message : 'Erreur réseau';
    return rdHttpError(0, null, msg, true);
  }
  const text = await res.text();
  const json = parseJsonText(text);
  if (!res.ok) {
    return rdHttpError(res.status, json, text || res.statusText);
  }
  if (!Array.isArray(json)) {
    return rdHttpError(res.status, json, 'Réponse postes partagés invalide (tableau attendu)');
  }
  const data: RegisteredDeviceAdminRowDto[] = [];
  for (const row of json) {
    const item = parseDeviceRow(row);
    if (item) data.push(item);
  }
  return { ok: true, data };
}

/** GET /v1/registered-devices/{device_id} */
export async function getRegisteredDeviceByIdForAdmin(
  auth: Pick<AuthContextPort, 'getAccessToken'>,
  deviceId: string,
  signal?: AbortSignal,
): Promise<RegisteredDeviceMutationResult> {
  const base = getLiveSnapshotBasePrefix();
  const url = `${base}/v1/registered-devices/${encodeURIComponent(deviceId.trim())}`;
  let res: Response;
  try {
    res = await fetch(url, { method: 'GET', credentials: 'include', headers: authHeaders(auth), signal });
  } catch (e) {
    const msg = e instanceof Error ? e.message : 'Erreur réseau';
    return rdHttpError(0, null, msg, true);
  }
  const text = await res.text();
  const json = parseJsonText(text);
  if (!res.ok) {
    return rdHttpError(res.status, json, text || res.statusText);
  }
  const device = parseDeviceRow(json);
  if (!device) return rdHttpError(res.status, json, 'Réponse poste partagé invalide');
  return { ok: true, device };
}

/** POST /v1/registered-devices/ */
export async function createRegisteredDeviceForAdmin(
  auth: Pick<AuthContextPort, 'getAccessToken'>,
  body: RegisteredDeviceAdminCreateBody,
  signal?: AbortSignal,
): Promise<RegisteredDeviceMutationResult> {
  const base = getLiveSnapshotBasePrefix();
  const url = `${base}/v1/registered-devices/`;
  let res: Response;
  try {
    res = await fetch(url, {
      method: 'POST',
      credentials: 'include',
      headers: authHeaders(auth, { 'Content-Type': 'application/json' }),
      body: JSON.stringify(body),
      signal,
    });
  } catch (e) {
    const msg = e instanceof Error ? e.message : 'Erreur réseau';
    return rdHttpError(0, null, msg, true);
  }
  const text = await res.text();
  const json = parseJsonText(text);
  if (!res.ok) {
    return rdHttpError(res.status, json, text || res.statusText);
  }
  const device = parseDeviceRow(json);
  if (!device) return rdHttpError(res.status, json, 'Réponse poste invalide');
  return { ok: true, device };
}

/** PATCH /v1/registered-devices/{device_id} */
export async function updateRegisteredDeviceForAdmin(
  auth: Pick<AuthContextPort, 'getAccessToken'>,
  deviceId: string,
  body: RegisteredDeviceAdminUpdateBody,
  signal?: AbortSignal,
): Promise<RegisteredDeviceMutationResult> {
  const base = getLiveSnapshotBasePrefix();
  const url = `${base}/v1/registered-devices/${encodeURIComponent(deviceId)}`;
  let res: Response;
  try {
    res = await fetch(url, {
      method: 'PATCH',
      credentials: 'include',
      headers: authHeaders(auth, { 'Content-Type': 'application/json' }),
      body: JSON.stringify(body),
      signal,
    });
  } catch (e) {
    const msg = e instanceof Error ? e.message : 'Erreur réseau';
    return rdHttpError(0, null, msg, true);
  }
  const text = await res.text();
  const json = parseJsonText(text);
  if (!res.ok) {
    return rdHttpError(res.status, json, text || res.statusText);
  }
  const device = parseDeviceRow(json);
  if (!device) return rdHttpError(res.status, json, 'Réponse poste invalide');
  return { ok: true, device };
}

/** POST /v1/registered-devices/{device_id}/revoke */
export async function revokeRegisteredDeviceForAdmin(
  auth: Pick<AuthContextPort, 'getAccessToken'>,
  deviceId: string,
  body: RegisteredDeviceRevokeBody = {},
  signal?: AbortSignal,
): Promise<RegisteredDeviceMutationResult> {
  const base = getLiveSnapshotBasePrefix();
  const url = `${base}/v1/registered-devices/${encodeURIComponent(deviceId)}/revoke`;
  let res: Response;
  try {
    res = await fetch(url, {
      method: 'POST',
      credentials: 'include',
      headers: authHeaders(auth, { 'Content-Type': 'application/json' }),
      body: JSON.stringify(body),
      signal,
    });
  } catch (e) {
    const msg = e instanceof Error ? e.message : 'Erreur réseau';
    return rdHttpError(0, null, msg, true);
  }
  const text = await res.text();
  const json = parseJsonText(text);
  if (!res.ok) {
    return rdHttpError(res.status, json, text || res.statusText);
  }
  const device = parseDeviceRow(json);
  if (!device) return rdHttpError(res.status, json, 'Réponse poste invalide');
  return { ok: true, device };
}

export type DeviceEnrollmentCodeIssueBody = {
  purpose: 'initial_enrollment' | 'reconnect' | 'replace';
};

export type DeviceEnrollmentCodeIssueResult =
  | { ok: true; code: string; expires_at: string; purpose: string }
  | RegisteredDevicesHttpError;

export type DeviceConflictResolveBody = {
  action: 'refuse' | 'replace_definitively' | 'create_distinct';
  name?: string;
};

/** POST /v1/registered-devices/{device_id}/enrollment-codes */
export async function issueDeviceEnrollmentCodeForAdmin(
  auth: Pick<AuthContextPort, 'getAccessToken'>,
  deviceId: string,
  body: DeviceEnrollmentCodeIssueBody,
  signal?: AbortSignal,
): Promise<DeviceEnrollmentCodeIssueResult> {
  const base = getLiveSnapshotBasePrefix();
  const url = `${base}/v1/registered-devices/${encodeURIComponent(deviceId)}/enrollment-codes`;
  let res: Response;
  try {
    res = await fetch(url, {
      method: 'POST',
      credentials: 'include',
      headers: authHeaders(auth, { 'Content-Type': 'application/json' }),
      body: JSON.stringify(body),
      signal,
    });
  } catch (e) {
    const msg = e instanceof Error ? e.message : 'Erreur réseau';
    return rdHttpError(0, null, msg, true);
  }
  const text = await res.text();
  const json = parseJsonText(text);
  if (!res.ok) return rdHttpError(res.status, json, text || res.statusText);
  if (!isRecord(json) || typeof json.code !== 'string') {
    return rdHttpError(res.status, json, 'Réponse code enrôlement invalide');
  }
  return {
    ok: true,
    code: json.code,
    expires_at: String(json.expires_at ?? ''),
    purpose: String(json.purpose ?? body.purpose),
  };
}

/** POST /v1/registered-devices/{device_id}/mark-identity-lost */
export async function markDeviceIdentityLostForAdmin(
  auth: Pick<AuthContextPort, 'getAccessToken'>,
  deviceId: string,
  signal?: AbortSignal,
): Promise<RegisteredDeviceMutationResult> {
  const base = getLiveSnapshotBasePrefix();
  const url = `${base}/v1/registered-devices/${encodeURIComponent(deviceId)}/mark-identity-lost`;
  let res: Response;
  try {
    res = await fetch(url, {
      method: 'POST',
      credentials: 'include',
      headers: authHeaders(auth),
      signal,
    });
  } catch (e) {
    const msg = e instanceof Error ? e.message : 'Erreur réseau';
    return rdHttpError(0, null, msg, true);
  }
  const text = await res.text();
  const json = parseJsonText(text);
  if (!res.ok) return rdHttpError(res.status, json, text || res.statusText);
  const device = parseDeviceRow(json);
  if (!device) return rdHttpError(res.status, json, 'Réponse poste invalide');
  return { ok: true, device };
}

/** POST /v1/registered-devices/{device_id}/resolve-conflict */
export async function resolveDeviceConflictForAdmin(
  auth: Pick<AuthContextPort, 'getAccessToken'>,
  deviceId: string,
  body: DeviceConflictResolveBody,
  signal?: AbortSignal,
): Promise<
  | {
      ok: true;
      device_id: string;
      status: string;
      distinct_device_id?: string | null;
      enrollment_code?: string | null;
      enrollment_code_expires_at?: string | null;
      enrollment_code_purpose?: string | null;
    }
  | RegisteredDevicesHttpError
> {
  const base = getLiveSnapshotBasePrefix();
  const url = `${base}/v1/registered-devices/${encodeURIComponent(deviceId)}/resolve-conflict`;
  let res: Response;
  try {
    res = await fetch(url, {
      method: 'POST',
      credentials: 'include',
      headers: authHeaders(auth, { 'Content-Type': 'application/json' }),
      body: JSON.stringify(body),
      signal,
    });
  } catch (e) {
    const msg = e instanceof Error ? e.message : 'Erreur réseau';
    return rdHttpError(0, null, msg, true);
  }
  const text = await res.text();
  const json = parseJsonText(text);
  if (!res.ok) return rdHttpError(res.status, json, text || res.statusText);
  if (!isRecord(json) || typeof json.device_id !== 'string') {
    return rdHttpError(res.status, json, 'Réponse résolution conflit invalide');
  }
  return {
    ok: true,
    device_id: json.device_id,
    status: String(json.status ?? ''),
    distinct_device_id: typeof json.distinct_device_id === 'string' ? json.distinct_device_id : null,
    enrollment_code: typeof json.enrollment_code === 'string' ? json.enrollment_code : null,
    enrollment_code_expires_at:
      typeof json.enrollment_code_expires_at === 'string' ? json.enrollment_code_expires_at : null,
    enrollment_code_purpose:
      typeof json.enrollment_code_purpose === 'string' ? json.enrollment_code_purpose : null,
  };
}
