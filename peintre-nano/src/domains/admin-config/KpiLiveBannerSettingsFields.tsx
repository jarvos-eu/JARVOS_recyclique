import { NumberInput, Stack, Switch } from '@mantine/core';
import {
  KPI_LIVE_BANNER_REFRESH_MAX_MS,
  KPI_LIVE_BANNER_REFRESH_MIN_MS,
  type KpiLiveBannerSettings,
} from '../bandeau-live/kpi-live-banner-settings';

export type KpiLiveBannerSettingsFieldsProps = {
  readonly value: KpiLiveBannerSettings;
  readonly onChange: (partial: Partial<KpiLiveBannerSettings>) => void;
  readonly disabled?: boolean;
};

/** Champs réglages bandeau KPI (contrôlé) — partagés admin modules / widget legacy. */
export function KpiLiveBannerSettingsFields({
  value,
  onChange,
  disabled = false,
}: KpiLiveBannerSettingsFieldsProps) {
  const minS = KPI_LIVE_BANNER_REFRESH_MIN_MS / 1000;
  const maxS = KPI_LIVE_BANNER_REFRESH_MAX_MS / 1000;
  const intervalSeconds = value.refreshIntervalMs / 1000;

  return (
    <Stack gap="md" data-testid="kpi-live-banner-settings-fields">
      <Switch
        label="Afficher sur la caisse (kiosque vente)"
        description="Bandeau sous l’en-tête de session sur l’écran de vente."
        checked={value.showOnCaisse}
        disabled={disabled}
        onChange={(e) => onChange({ showOnCaisse: e.currentTarget.checked })}
        data-testid="admin-kpi-live-toggle-caisse"
      />
      <Switch
        label="Afficher sur la réception"
        description="Bandeau dans le chrome de l’écran réception."
        checked={value.showOnReception}
        disabled={disabled}
        onChange={(e) => onChange({ showOnReception: e.currentTarget.checked })}
        data-testid="admin-kpi-live-toggle-reception"
      />
      <NumberInput
        label="Période de rafraîchissement (secondes)"
        description={`Entre ${minS} et ${maxS} secondes (plancher aligné sur l’API unifiée).`}
        min={minS}
        max={maxS}
        disabled={disabled}
        value={intervalSeconds}
        onChange={(v) => {
          const n = typeof v === 'number' ? v : Number(v);
          if (!Number.isFinite(n)) return;
          onChange({ refreshIntervalMs: Math.round(n * 1000) });
        }}
        data-testid="admin-kpi-live-refresh-seconds"
      />
    </Stack>
  );
}
