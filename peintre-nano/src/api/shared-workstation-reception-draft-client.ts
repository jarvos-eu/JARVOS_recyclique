import { getLiveSnapshotBasePrefix } from './live-snapshot-client';
import { parseRecycliqueApiErrorBody, toRecycliqueClientFailure } from './recyclique-api-error';
import { sharedWorkstationAuthHeaders } from '../domains/shared-workstation/device-identity-store';

export type ReceptionDraftSummary = {
  readonly poste_id: string;
  readonly ticket_id: string;
  readonly started_by_display: string;
  readonly started_at: string;
  readonly line_count: number;
};

export type ReceptionDraftFetchResult =
  | { ok: true; summary: ReceptionDraftSummary | null }
  | { ok: false; status: number; message: string; code?: string };

export type ReceptionDraftActionResult =
  | { ok: true; poste_id?: string; ticket_id?: string }
  | { ok: false; status: number; message: string; code?: string };

function parseJsonText(text: string): unknown {
  if (!text) return null;
  try {
    return JSON.parse(text) as unknown;
  } catch {
    return null;
  }
}

async function draftHeaders(accessToken: string): Promise<Record<string, string>> {
  const deviceHeaders = await sharedWorkstationAuthHeaders();
  return {
    Accept: 'application/json',
    Authorization: `Bearer ${accessToken}`,
    'Content-Type': 'application/json',
    ...deviceHeaders,
  };
}

/** GET /v1/shared-workstation/reception-draft — Story 27.8 */
export async function fetchSharedWorkstationReceptionDraft(
  accessToken: string,
  signal?: AbortSignal,
): Promise<ReceptionDraftFetchResult> {
  const base = getLiveSnapshotBasePrefix();
  const url = `${base}/v1/shared-workstation/reception-draft`;
  let res: Response;
  try {
    res = await fetch(url, {
      method: 'GET',
      cache: 'no-store',
      credentials: 'include',
      signal,
      headers: await draftHeaders(accessToken),
    });
  } catch (e) {
    const msg = e instanceof Error ? e.message : 'Erreur réseau';
    return { ok: false, status: 0, message: msg };
  }
  if (res.status === 204) {
    return { ok: true, summary: null };
  }
  const text = await res.text();
  const json = parseJsonText(text);
  if (!res.ok) {
    const p = parseRecycliqueApiErrorBody(json, res.status, text || res.statusText);
    const f = toRecycliqueClientFailure(res.status, p, false);
    return { ok: false, status: res.status, message: f.message, code: f.code };
  }
  if (!json || typeof json !== 'object') {
    return { ok: false, status: res.status, message: 'Réponse brouillon invalide' };
  }
  const row = json as Record<string, unknown>;
  const summaryRaw = row.summary;
  if (!summaryRaw || typeof summaryRaw !== 'object') {
    return { ok: false, status: res.status, message: 'Résumé brouillon invalide' };
  }
  const s = summaryRaw as Record<string, unknown>;
  if (
    typeof s.poste_id !== 'string' ||
    typeof s.ticket_id !== 'string' ||
    typeof s.started_by_display !== 'string' ||
    typeof s.started_at !== 'string' ||
    typeof s.line_count !== 'number'
  ) {
    return { ok: false, status: res.status, message: 'Résumé brouillon incomplet' };
  }
  return {
    ok: true,
    summary: {
      poste_id: s.poste_id,
      ticket_id: s.ticket_id,
      started_by_display: s.started_by_display,
      started_at: s.started_at,
      line_count: s.line_count,
    },
  };
}

export async function resumeSharedWorkstationReceptionDraft(
  accessToken: string,
): Promise<ReceptionDraftActionResult> {
  const base = getLiveSnapshotBasePrefix();
  const url = `${base}/v1/shared-workstation/reception-draft/resume`;
  let res: Response;
  try {
    res = await fetch(url, {
      method: 'POST',
      cache: 'no-store',
      credentials: 'include',
      headers: await draftHeaders(accessToken),
      body: JSON.stringify({ confirm: true }),
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
    return { ok: false, status: res.status, message: 'Réponse reprise invalide' };
  }
  const row = json as Record<string, unknown>;
  if (typeof row.poste_id !== 'string' || typeof row.ticket_id !== 'string') {
    return { ok: false, status: res.status, message: 'Réponse reprise incomplète' };
  }
  return { ok: true, poste_id: row.poste_id, ticket_id: row.ticket_id };
}

export async function abandonSharedWorkstationReceptionDraft(
  accessToken: string,
): Promise<ReceptionDraftActionResult> {
  const base = getLiveSnapshotBasePrefix();
  const url = `${base}/v1/shared-workstation/reception-draft/abandon`;
  let res: Response;
  try {
    res = await fetch(url, {
      method: 'POST',
      cache: 'no-store',
      credentials: 'include',
      headers: await draftHeaders(accessToken),
      body: JSON.stringify({ confirm: true }),
    });
  } catch (e) {
    const msg = e instanceof Error ? e.message : 'Erreur réseau';
    return { ok: false, status: 0, message: msg };
  }
  if (!res.ok) {
    const text = await res.text();
    const json = parseJsonText(text);
    const p = parseRecycliqueApiErrorBody(json, res.status, text || res.statusText);
    const f = toRecycliqueClientFailure(res.status, p, false);
    return { ok: false, status: res.status, message: f.message, code: f.code };
  }
  return { ok: true };
}
