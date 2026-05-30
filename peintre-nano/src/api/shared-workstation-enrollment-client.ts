import { getLiveSnapshotBasePrefix } from './live-snapshot-client';
import { parseRecycliqueApiErrorBody, toRecycliqueClientFailure } from './recyclique-api-error';

export type EnrollCompleteBody = {
  readonly code: string;
};

export type EnrollCompleteResult =
  | {
      ok: true;
      device_id: string;
      device_secret: string;
      device_name: string;
      site_id: string;
    }
  | {
      ok: false;
      status: number;
      message: string;
      code?: string;
    };

function parseJsonText(text: string): unknown {
  if (!text) return null;
  try {
    return JSON.parse(text) as unknown;
  } catch {
    return null;
  }
}

/** POST /v1/shared-workstation/enroll/complete — semi-public (sans Bearer). */
export async function completeSharedWorkstationEnrollment(
  body: EnrollCompleteBody,
  signal?: AbortSignal,
): Promise<EnrollCompleteResult> {
  const base = getLiveSnapshotBasePrefix();
  const url = `${base}/v1/shared-workstation/enroll/complete`;
  let res: Response;
  try {
    res = await fetch(url, {
      method: 'POST',
      credentials: 'include',
      headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
      body: JSON.stringify({ code: body.code.trim().toUpperCase() }),
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
    return { ok: false, status: res.status, message: 'Réponse enrôlement invalide' };
  }
  const row = json as Record<string, unknown>;
  const device_id = row.device_id;
  const device_secret = row.device_secret;
  const device_name = row.device_name;
  const site_id = row.site_id;
  if (
    typeof device_id !== 'string' ||
    typeof device_secret !== 'string' ||
    typeof device_name !== 'string' ||
    typeof site_id !== 'string'
  ) {
    return { ok: false, status: res.status, message: 'Réponse enrôlement incomplète' };
  }
  return { ok: true, device_id, device_secret, device_name, site_id };
}
