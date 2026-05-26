import type { AuthContextPort } from '../app/auth/auth-context-port';
import { getLiveSnapshotBasePrefix } from './live-snapshot-client';
import { parseRecycliqueApiErrorBody, toRecycliqueClientFailure } from './recyclique-api-error';

export const KPI_LIVE_BANNER_MODULE_KEY = 'kpi-live-banner' as const;
export const KPI_LIVE_BANNER_SCHEMA_VERSION = '1.0.0' as const;

/** Aligné OpenAPI `ModuleConfigDocument`. */
export type ModuleConfigDocumentDto = {
  readonly schema_version: string;
  readonly payload: Record<string, unknown>;
  readonly version?: number;
};

export type KpiLiveBannerPayloadDto = {
  readonly show_on_caisse: boolean;
  readonly show_on_reception: boolean;
  readonly refresh_interval_seconds: number;
};

type ModuleConfigHttpError = {
  ok: false;
  status: number;
  detail: string;
  code?: string;
  retryable?: boolean;
  state?: string | null;
  correlation_id?: string;
  networkError?: boolean;
};

function moduleConfigHttpError(
  status: number,
  json: unknown,
  fallbackDetail: string,
  networkError?: boolean,
): ModuleConfigHttpError {
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

export function parseModuleConfigDocument(json: unknown): ModuleConfigDocumentDto | null {
  if (!isRecord(json)) return null;
  const schema_version = json.schema_version;
  const payload = json.payload;
  if (typeof schema_version !== 'string' || !isRecord(payload)) return null;
  const version = json.version;
  return {
    schema_version,
    payload,
    version: typeof version === 'number' && Number.isFinite(version) ? version : undefined,
  };
}

/** Extrait l’ETag HTTP (RFC 7232) — ex. `W/"1"`. */
export function parseEtagFromResponse(res: Response): string | null {
  const raw = res.headers.get('ETag') ?? res.headers.get('etag');
  if (!raw) return null;
  const trimmed = raw.trim();
  return trimmed.length > 0 ? trimmed : null;
}

/** Parse la version entière depuis un ETag `W/"n"` ou `"n"`. */
export function parseEtagVersion(etag: string | null | undefined): number | null {
  if (!etag) return null;
  let raw = etag.trim();
  if (raw.startsWith('W/')) raw = raw.slice(2).trim();
  if (raw.length >= 2 && raw.startsWith('"') && raw.endsWith('"')) raw = raw.slice(1, -1);
  const n = Number.parseInt(raw, 10);
  return Number.isFinite(n) ? n : null;
}

export function formatIfMatchFromEtag(etag: string | null | undefined): string | undefined {
  if (!etag?.trim()) return undefined;
  return etag.trim();
}

function moduleConfigUrl(siteId: string, moduleKey: string): string {
  const base = getLiveSnapshotBasePrefix();
  return `${base}/v1/sites/${encodeURIComponent(siteId)}/module-config/${encodeURIComponent(moduleKey)}`;
}

export type GetSiteModuleConfigResult =
  | { ok: true; data: ModuleConfigDocumentDto; etag: string | null }
  | ModuleConfigHttpError;

/** `GET /v1/sites/{site_id}/module-config/{module_key}` — `recyclique_moduleConfig_getSiteModuleConfig`. */
export async function getSiteModuleConfig(
  auth: Pick<AuthContextPort, 'getAccessToken'>,
  siteId: string,
  moduleKey: string,
  signal?: AbortSignal,
): Promise<GetSiteModuleConfigResult> {
  const url = moduleConfigUrl(siteId, moduleKey);
  let res: Response;
  try {
    res = await fetch(url, { method: 'GET', credentials: 'include', headers: authHeaders(auth), signal });
  } catch (e) {
    const msg = e instanceof Error ? e.message : 'Erreur réseau';
    return moduleConfigHttpError(0, null, msg, true);
  }
  const text = await res.text();
  const json = parseJsonText(text);
  if (!res.ok) {
    return moduleConfigHttpError(res.status, json, text || res.statusText);
  }
  const data = parseModuleConfigDocument(json);
  if (!data) {
    return moduleConfigHttpError(res.status, json, 'Réponse configuration module invalide');
  }
  return { ok: true, data, etag: parseEtagFromResponse(res) };
}

export type PatchSiteModuleConfigResult =
  | { ok: true; data: ModuleConfigDocumentDto; etag: string | null }
  | ModuleConfigHttpError;

/** `PATCH /v1/sites/{site_id}/module-config/{module_key}` — `recyclique_moduleConfig_patchSiteModuleConfig`. */
export async function patchSiteModuleConfig(
  auth: Pick<AuthContextPort, 'getAccessToken'>,
  siteId: string,
  moduleKey: string,
  body: ModuleConfigDocumentDto,
  options?: {
    readonly ifMatch?: string | null;
    readonly signal?: AbortSignal;
    readonly changeReason?: string;
  },
): Promise<PatchSiteModuleConfigResult> {
  const url = moduleConfigUrl(siteId, moduleKey);
  const extra: Record<string, string> = { 'Content-Type': 'application/json' };
  const ifMatch = formatIfMatchFromEtag(options?.ifMatch);
  if (ifMatch) extra['If-Match'] = ifMatch;
  const reason = options?.changeReason?.trim();
  if (reason) extra['X-Module-Config-Change-Reason'] = reason;
  let res: Response;
  try {
    res = await fetch(url, {
      method: 'PATCH',
      credentials: 'include',
      headers: authHeaders(auth, extra),
      body: JSON.stringify(body),
      signal: options?.signal,
    });
  } catch (e) {
    const msg = e instanceof Error ? e.message : 'Erreur réseau';
    return moduleConfigHttpError(0, null, msg, true);
  }
  const text = await res.text();
  const json = parseJsonText(text);
  if (!res.ok) {
    return moduleConfigHttpError(res.status, json, text || res.statusText);
  }
  const data = parseModuleConfigDocument(json);
  if (!data) {
    return moduleConfigHttpError(res.status, json, 'Réponse mise à jour module invalide');
  }
  return { ok: true, data, etag: parseEtagFromResponse(res) };
}

export function parseKpiLiveBannerPayload(payload: Record<string, unknown>): KpiLiveBannerPayloadDto | null {
  const show_on_caisse = payload.show_on_caisse;
  const show_on_reception = payload.show_on_reception;
  const refresh_interval_seconds = payload.refresh_interval_seconds;
  if (typeof show_on_caisse !== 'boolean' || typeof show_on_reception !== 'boolean') return null;
  if (typeof refresh_interval_seconds !== 'number' || !Number.isFinite(refresh_interval_seconds)) return null;
  return { show_on_caisse, show_on_reception, refresh_interval_seconds };
}

export function buildKpiLiveBannerModuleDocument(
  payload: KpiLiveBannerPayloadDto,
  version?: number,
): ModuleConfigDocumentDto {
  return {
    schema_version: KPI_LIVE_BANNER_SCHEMA_VERSION,
    payload: { ...payload },
    ...(version !== undefined ? { version } : {}),
  };
}
