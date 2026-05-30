import { getLiveSnapshotBasePrefix } from './live-snapshot-client';
import { parseRecycliqueApiErrorBody, toRecycliqueClientFailure } from './recyclique-api-error';
import { sharedWorkstationAuthHeaders } from '../domains/shared-workstation/device-identity-store';

export type OverrideDeactivateReason = 'user_exit' | 'admin_action';

export type ActivateOverrideResult =
  | {
      ok: true;
      override_active: boolean;
      override_started_at: string;
      override_expires_at: string;
    }
  | { ok: false; status: number; message: string; code?: string };

export type DeactivateOverrideResult =
  | { ok: true; override_active: boolean }
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

/** POST /v1/shared-workstation/override/activate */
export async function activateOverride(
  confirmationPin: string,
  signal?: AbortSignal,
): Promise<ActivateOverrideResult> {
  const base = getLiveSnapshotBasePrefix();
  const url = `${base}/v1/shared-workstation/override/activate`;
  let res: Response;
  try {
    res = await deviceFetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ confirmation_pin: confirmationPin }),
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
    return { ok: false, status: res.status, message: 'Réponse activation override invalide' };
  }
  const row = json as Record<string, unknown>;
  if (
    typeof row.override_started_at !== 'string' ||
    typeof row.override_expires_at !== 'string'
  ) {
    return { ok: false, status: res.status, message: 'Réponse activation override incomplète' };
  }
  return {
    ok: true,
    override_active: Boolean(row.override_active),
    override_started_at: row.override_started_at,
    override_expires_at: row.override_expires_at,
  };
}

/** POST /v1/shared-workstation/override/deactivate */
export async function deactivateOverride(
  reason: OverrideDeactivateReason = 'user_exit',
  signal?: AbortSignal,
): Promise<DeactivateOverrideResult> {
  const base = getLiveSnapshotBasePrefix();
  const url = `${base}/v1/shared-workstation/override/deactivate`;
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
    return { ok: false, status: res.status, message: 'Réponse désactivation override invalide' };
  }
  const row = json as Record<string, unknown>;
  return { ok: true, override_active: Boolean(row.override_active) };
}
