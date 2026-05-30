import { getLiveSnapshotBasePrefix } from './live-snapshot-client';
import { parseRecycliqueApiErrorBody, toRecycliqueClientFailure } from './recyclique-api-error';
import { sharedWorkstationAuthHeaders } from '../domains/shared-workstation/device-identity-store';

import {
  fetchOperatorSessionStatus as fetchOperatorSessionStatusEnriched,
  type OperatorSessionStatus as EnrichedOperatorSessionStatus,
} from './shared-workstation-operator-session-client';

export type OperatorSessionStatus =
  | {
      ok: true;
      active: boolean;
      operator_user_id: string | null;
      session_id: string | null;
    }
  | { ok: false; status: number; message: string; code?: string };

/** @deprecated Prefer shared-workstation-operator-session-client for enriched fields. */
export async function fetchOperatorSessionStatus(
  signal?: AbortSignal,
): Promise<OperatorSessionStatus> {
  const status: EnrichedOperatorSessionStatus = await fetchOperatorSessionStatusEnriched(signal);
  if (!status.ok) return status;
  return {
    ok: true,
    active: status.active,
    operator_user_id: status.operator_user_id,
    session_id: status.session_id,
  };
}

export type VerifyOperatorPinBody = {
  readonly operator_user_id: string;
  readonly pin: string;
};

export type VerifyOperatorPinResult =
  | {
      ok: true;
      session_id: string;
      device_id: string;
      operator_user_id: string;
      site_id: string;
      started_at: string;
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

/** POST /v1/shared-workstation/operator-pin/verify */
export async function verifySharedWorkstationOperatorPin(
  body: VerifyOperatorPinBody,
  signal?: AbortSignal,
): Promise<VerifyOperatorPinResult> {
  const base = getLiveSnapshotBasePrefix();
  const url = `${base}/v1/shared-workstation/operator-pin/verify`;
  let res: Response;
  try {
    res = await deviceFetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        operator_user_id: body.operator_user_id.trim(),
        pin: body.pin,
      }),
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
    return { ok: false, status: res.status, message: 'Réponse PIN invalide' };
  }
  const row = json as Record<string, unknown>;
  const session_id = row.session_id;
  const device_id = row.device_id;
  const operator_user_id = row.operator_user_id;
  const site_id = row.site_id;
  const started_at = row.started_at;
  if (
    typeof session_id !== 'string' ||
    typeof device_id !== 'string' ||
    typeof operator_user_id !== 'string' ||
    typeof site_id !== 'string' ||
    typeof started_at !== 'string'
  ) {
    return { ok: false, status: res.status, message: 'Réponse PIN incomplète' };
  }
  return {
    ok: true,
    session_id,
    device_id,
    operator_user_id,
    site_id,
    started_at,
  };
}
