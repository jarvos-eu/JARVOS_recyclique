/** Fixture 15 lignes — aligné backend seed Story 9.11. */
export const FIXTURE_CASH_DENOMINATIONS = [
  { code: 'EUR_50000', label_fr: '500 €', kind: 'note', unit_value_cents: 50000, display_order: 1, display_default: false },
  { code: 'EUR_20000', label_fr: '200 €', kind: 'note', unit_value_cents: 20000, display_order: 2, display_default: true },
  { code: 'EUR_10000', label_fr: '100 €', kind: 'note', unit_value_cents: 10000, display_order: 3, display_default: true },
  { code: 'EUR_5000', label_fr: '50 €', kind: 'note', unit_value_cents: 5000, display_order: 4, display_default: true },
  { code: 'EUR_2000', label_fr: '20 €', kind: 'note', unit_value_cents: 2000, display_order: 5, display_default: true },
  { code: 'EUR_1000', label_fr: '10 €', kind: 'note', unit_value_cents: 1000, display_order: 6, display_default: true },
  { code: 'EUR_500', label_fr: '5 €', kind: 'note', unit_value_cents: 500, display_order: 7, display_default: true },
  { code: 'EUR_200', label_fr: '2 €', kind: 'coin', unit_value_cents: 200, display_order: 8, display_default: true },
  { code: 'EUR_100', label_fr: '1 €', kind: 'coin', unit_value_cents: 100, display_order: 9, display_default: true },
  { code: 'EUR_050', label_fr: '50 c', kind: 'coin', unit_value_cents: 50, display_order: 10, display_default: true },
  { code: 'EUR_020', label_fr: '20 c', kind: 'coin', unit_value_cents: 20, display_order: 11, display_default: true },
  { code: 'EUR_010', label_fr: '10 c', kind: 'coin', unit_value_cents: 10, display_order: 12, display_default: true },
  { code: 'EUR_005', label_fr: '5 c', kind: 'coin', unit_value_cents: 5, display_order: 13, display_default: true },
  { code: 'EUR_002', label_fr: '2 c', kind: 'coin', unit_value_cents: 2, display_order: 14, display_default: true },
  { code: 'EUR_001', label_fr: '1 c', kind: 'coin', unit_value_cents: 1, display_order: 15, display_default: true },
] as const;

export function denominationCountResponseForTotal(totalCents: number) {
  const lines =
    totalCents >= 2000
      ? [{ code: 'EUR_2000', quantity: Math.floor(totalCents / 2000), unit_value_cents: 2000, line_total_cents: Math.floor(totalCents / 2000) * 2000 }]
      : [{ code: 'EUR_100', quantity: 0, unit_value_cents: 100, line_total_cents: 0 }];
  const theoretical = 7500;
  return {
    denominations: FIXTURE_CASH_DENOMINATIONS,
    breakdown: lines,
    total_counted_cents: totalCents,
    theoretical_cash_cents: theoretical,
    variance_cents: totalCents - theoretical,
    float_target_cents: 5000,
    withdraw_cents: Math.max(0, totalCents - 5000),
    recorded_at: '2026-06-06T18:00:00Z',
    has_count_recorded: true,
  };
}

export function comptageModuleEnabledJson(showImages = true) {
  return comptageModulePilotJson(showImages);
}

/** Defaults safe Story 9.13 AC4 — module off, parité legacy. */
export function comptageModuleDisabledJson() {
  return {
    schema_version: '1.0.0',
    payload: {
      enabled: false,
      skip_allowed: true,
      require_denomination_grid: false,
      show_images: true,
    },
    version: 0,
  };
}

/** Config pilote La Clique Story 9.13 AC8 / Q-HITL-11. */
export function comptageModulePilotJson(showImages = true) {
  return {
    schema_version: '1.0.0',
    payload: {
      enabled: true,
      skip_allowed: false,
      require_denomination_grid: true,
      show_images: showImages,
    },
    version: 1,
  };
}
