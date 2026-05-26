import { UNIFIED_LIVE_KPI_POLL_INTERVAL_MS } from './use-unified-live-kpi-poll';

export type KpiLiveBannerSettings = {
  showOnCaisse: boolean;
  showOnReception: boolean;
  refreshIntervalMs: number;
};

/** Bornes schéma API `kpi-live-banner.v1.json` (secondes). */
export const KPI_LIVE_BANNER_REFRESH_MIN_SECONDS = 15;
export const KPI_LIVE_BANNER_REFRESH_MAX_SECONDS = 3600;

export const KPI_LIVE_BANNER_REFRESH_MIN_MS = KPI_LIVE_BANNER_REFRESH_MIN_SECONDS * 1000;
export const KPI_LIVE_BANNER_REFRESH_MAX_MS = KPI_LIVE_BANNER_REFRESH_MAX_SECONDS * 1000;

export const KPI_LIVE_BANNER_DEFAULTS: KpiLiveBannerSettings = {
  showOnCaisse: true,
  showOnReception: true,
  refreshIntervalMs: 60_000,
};

function clampInterval(ms: number): number {
  if (!Number.isFinite(ms)) return KPI_LIVE_BANNER_DEFAULTS.refreshIntervalMs;
  return Math.min(
    KPI_LIVE_BANNER_REFRESH_MAX_MS,
    Math.max(KPI_LIVE_BANNER_REFRESH_MIN_MS, Math.round(ms)),
  );
}

function clampRefreshSeconds(seconds: number): number {
  if (!Number.isFinite(seconds)) return KPI_LIVE_BANNER_DEFAULTS.refreshIntervalMs / 1000;
  return Math.min(
    KPI_LIVE_BANNER_REFRESH_MAX_SECONDS,
    Math.max(KPI_LIVE_BANNER_REFRESH_MIN_SECONDS, Math.round(seconds)),
  );
}

export type KpiLiveBannerPayloadApi = {
  readonly show_on_caisse: boolean;
  readonly show_on_reception: boolean;
  readonly refresh_interval_seconds: number;
};

export function kpiLiveBannerPayloadToSettings(payload: KpiLiveBannerPayloadApi): KpiLiveBannerSettings {
  return {
    showOnCaisse: payload.show_on_caisse,
    showOnReception: payload.show_on_reception,
    refreshIntervalMs: clampInterval(clampRefreshSeconds(payload.refresh_interval_seconds) * 1000),
  };
}

export function kpiLiveBannerSettingsToPayload(settings: KpiLiveBannerSettings): KpiLiveBannerPayloadApi {
  return {
    show_on_caisse: settings.showOnCaisse,
    show_on_reception: settings.showOnReception,
    refresh_interval_seconds: clampRefreshSeconds(settings.refreshIntervalMs / 1000),
  };
}

export function mergeKpiLiveBannerSettings(
  base: KpiLiveBannerSettings,
  partial: Partial<KpiLiveBannerSettings>,
): KpiLiveBannerSettings {
  return {
    showOnCaisse: partial.showOnCaisse ?? base.showOnCaisse,
    showOnReception: partial.showOnReception ?? base.showOnReception,
    refreshIntervalMs:
      partial.refreshIntervalMs !== undefined ? clampInterval(partial.refreshIntervalMs) : base.refreshIntervalMs,
  };
}

/** Intervalle poll unifié caisse/réception (distinct du minimum admin schéma module). */
export { UNIFIED_LIVE_KPI_POLL_INTERVAL_MS };
