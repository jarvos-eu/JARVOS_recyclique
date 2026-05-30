import { getLiveSnapshotBasePrefix } from './live-snapshot-client';
import { parseRecycliqueApiErrorBody, toRecycliqueClientFailure } from './recyclique-api-error';
import { sharedWorkstationAuthHeaders } from '../domains/shared-workstation/device-identity-store';

export type OperatorSessionEndReason = 'manual_lock' | 'handoff' | 'timeout';

export type OperatorSessionStatus =
  | {
      ok: true;
      active: boolean;
      operator_user_id: string | null;
      session_id: string | null;
      last_activity_at: string | null;
      inactivity_timeout_seconds: number | null;
      seconds_until_lock: number | null;
      override_active: boolean;
      override_started_at: string | null;
      override_seconds_remaining: number | null;
      can_activate_super_admin_override: boolean;
    }
  | { ok: false; status: number; message: string; code?: string };

export type DeviceStatusResult =
  | {
      ok: true;
      device_id: string;
      inactivity_timeout_seconds: number;
    }
  | { ok: false; status: number; message: string; code?: string };

export type EndOperatorSessionResult =
  | { ok: true; ended: boolean; session_id: string | null }
  | { ok: false; status: number; message: string; code?: string };

export type TouchActivityResult =
  | { ok: true; throttled: boolean }
  | { ok: false; status: number; message: string; code?: string };

function parseJsonText(text: string): unknown {
  if (!text) return null;
  try {
    return JSON.parse(text) as unknown;
  } catch {
    return null;
  }
}

async function deviceFetch(url: string, init: RequestInit): Promise<Response> {
  const deviceHeaders = await sharedWorkstationAuthHeaders();
  const headers = {
    Accept: 'application/json',
    ...deviceHeaders,
    ...(init.headers as Record<string, string> | undefined),
  };
  return fetch(url, {
    ...init,
    cache: 'no-store',
    credentials: 'include',
    headers,
  });
}

/** GET /v1/shared-workstation/device-status */
export async function fetchSharedWorkstationDeviceStatus(
  signal?: AbortSignal,
): Promise<DeviceStatusResult> {
  const base = getLiveSnapshotBasePrefix();
  const url = `${base}/v1/shared-workstation/device-status`;
  let res: Response;
  try {
    res = await deviceFetch(url, { method: 'GET', signal });
  } catch (e) {
    const msg = e instanceof Error ? e.message : 'Erreur réseau';
    return { ok: false, status: 0, message: msg };
  }
  const text = await res.text();
  const json = parseJsonText(text);
  if (!res.ok) {
    const p = parseRecycliqueApiErrorBody(json, res.status, text || res.statusText);
    const f = toRecycliqueClientFailure(res.status, p, false);
    return { ok: false, status: res.status, message: f.message, code: f.code };
  }
  if (!json || typeof json !== 'object') {
    return { ok: false, status: res.status, message: 'Réponse device-status invalide' };
  }
  const row = json as Record<string, unknown>;
  const device_id = row.device_id;
  const timeout = row.inactivity_timeout_seconds;
  if (typeof device_id !== 'string' || typeof timeout !== 'number') {
    return { ok: false, status: res.status, message: 'Réponse device-status incomplète' };
  }
  return { ok: true, device_id, inactivity_timeout_seconds: timeout };
}

/** GET /v1/shared-workstation/operator-session/status (enrichi 27.9) */
export async function fetchOperatorSessionStatus(
  signal?: AbortSignal,
): Promise<OperatorSessionStatus> {
  const base = getLiveSnapshotBasePrefix();
  const url = `${base}/v1/shared-workstation/operator-session/status`;
  let res: Response;
  try {
    res = await deviceFetch(url, { method: 'GET', signal });
  } catch (e) {
    const msg = e instanceof Error ? e.message : 'Erreur réseau';
    return { ok: false, status: 0, message: msg };
  }
  const text = await res.text();
  const json = parseJsonText(text);
  if (!res.ok) {
    const p = parseRecycliqueApiErrorBody(json, res.status, text || res.statusText);
    const f = toRecycliqueClientFailure(res.status, p, false);
    return { ok: false, status: res.status, message: f.message, code: f.code };
  }
  if (!json || typeof json !== 'object') {
    return { ok: false, status: res.status, message: 'Réponse statut session invalide' };
  }
  const row = json as Record<string, unknown>;
  return {
    ok: true,
    active: Boolean(row.active),
    operator_user_id:
      typeof row.operator_user_id === 'string' ? row.operator_user_id : null,
    session_id: typeof row.session_id === 'string' ? row.session_id : null,
    last_activity_at:
      typeof row.last_activity_at === 'string' ? row.last_activity_at : null,
    inactivity_timeout_seconds:
      typeof row.inactivity_timeout_seconds === 'number'
        ? row.inactivity_timeout_seconds
        : null,
    seconds_until_lock:
      typeof row.seconds_until_lock === 'number' ? row.seconds_until_lock : null,
    override_active: Boolean(row.override_active),
    override_started_at:
      typeof row.override_started_at === 'string' ? row.override_started_at : null,
    override_seconds_remaining:
      typeof row.override_seconds_remaining === 'number'
        ? row.override_seconds_remaining
        : null,
    can_activate_super_admin_override: Boolean(row.can_activate_super_admin_override),
  };
}

/** POST /v1/shared-workstation/operator-session/end */
export async function endOperatorSession(
  reason: OperatorSessionEndReason,
  signal?: AbortSignal,
): Promise<EndOperatorSessionResult> {
  const base = getLiveSnapshotBasePrefix();
  const url = `${base}/v1/shared-workstation/operator-session/end`;
  let res: Response;
  try {
    res = await deviceFetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ reason }),
      signal,
    });
  } catch (e) {
    const msg = e instanceof Error ? e.message : 'Erreur réseau';
    return { ok: false, status: 0, message: msg };
  }
  const text = await res.text();
  const json = parseJsonText(text);
  if (!res.ok) {
    const p = parseRecycliqueApiErrorBody(json, res.status, text || res.statusText);
    const f = toRecycliqueClientFailure(res.status, p, false);
    return { ok: false, status: res.status, message: f.message, code: f.code };
  }
  if (!json || typeof json !== 'object') {
    return { ok: false, status: res.status, message: 'Réponse fin session invalide' };
  }
  const row = json as Record<string, unknown>;
  return {
    ok: true,
    ended: Boolean(row.ended),
    session_id: typeof row.session_id === 'string' ? row.session_id : null,
  };
}

/** POST /v1/shared-workstation/operator-session/activity */
export async function touchOperatorSessionActivity(
  signal?: AbortSignal,
): Promise<TouchActivityResult> {
  const base = getLiveSnapshotBasePrefix();
  const url = `${base}/v1/shared-workstation/operator-session/activity`;
  let res: Response;
  try {
    res = await deviceFetch(url, { method: 'POST', signal });
  } catch (e) {
    const msg = e instanceof Error ? e.message : 'Erreur réseau';
    return { ok: false, status: 0, message: msg };
  }
  if (res.status === 204 || res.ok) {
    return { ok: true, throttled: res.status === 204 };
  }
  const text = await res.text();
  const json = parseJsonText(text);
  const p = parseRecycliqueApiErrorBody(json, res.status, text || res.statusText);
  const f = toRecycliqueClientFailure(res.status, p, false);
  return { ok: false, status: res.status, message: f.message, code: f.code };
}
