import { getLiveSnapshotBasePrefix } from './live-snapshot-client';
import { parseRecycliqueApiErrorBody, toRecycliqueClientFailure } from './recyclique-api-error';
import { sharedWorkstationAuthHeaders } from '../domains/shared-workstation/device-identity-store';

export type EffectiveModulesResult =
  | {
      ok: true;
      module_keys: readonly string[];
      computed_at: string;
      site_id: string;
      device_id: string;
      operator_user_id: string;
    }
  | { ok: false; status: number; message: string; code?: string };

function parseJsonText(text: string): unknown {
  if (!text) return null;
  try {
    return JSON.parse(text) as unknown;
  } catch {
    return null;
  }
}

/** GET /v1/shared-workstation/effective-modules — Story 27.7 */
export async function fetchSharedWorkstationEffectiveModules(
  accessToken: string,
  signal?: AbortSignal,
): Promise<EffectiveModulesResult> {
  const base = getLiveSnapshotBasePrefix();
  const url = `${base}/v1/shared-workstation/effective-modules`;
  const deviceHeaders = await sharedWorkstationAuthHeaders();
  let res: Response;
  try {
    res = await fetch(url, {
      method: 'GET',
      cache: 'no-store',
      credentials: 'include',
      signal,
      headers: {
        Accept: 'application/json',
        Authorization: `Bearer ${accessToken}`,
        ...deviceHeaders,
      },
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
    return { ok: false, status: res.status, message: 'Réponse modules effectifs invalide' };
  }
  const row = json as Record<string, unknown>;
  const moduleKeys = row.module_keys;
  if (!Array.isArray(moduleKeys) || !moduleKeys.every((k) => typeof k === 'string')) {
    return { ok: false, status: res.status, message: 'module_keys invalide' };
  }
  const computed_at = row.computed_at;
  const site_id = row.site_id;
  const device_id = row.device_id;
  const operator_user_id = row.operator_user_id;
  if (
    typeof computed_at !== 'string' ||
    typeof site_id !== 'string' ||
    typeof device_id !== 'string' ||
    typeof operator_user_id !== 'string'
  ) {
    return { ok: false, status: res.status, message: 'Réponse modules effectifs incomplète' };
  }
  return {
    ok: true,
    module_keys: moduleKeys,
    computed_at,
    site_id,
    device_id,
    operator_user_id,
  };
}
